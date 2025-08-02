"""
Enhanced error handling for AI providers with intelligent retry strategies.

This module provides robust error handling, retry logic, and graceful degradation
for AI service failures.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, Callable, TypeVar, Union, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorType(Enum):
    """Types of errors that can occur with AI services."""

    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION = "authentication"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context about an error for better handling decisions."""

    error_type: ErrorType
    error_message: str
    provider: str
    model: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    attempt_number: int = 1
    original_exception: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RetryStrategy:
    """Base class for retry strategies."""
    
    def should_retry(self, context: ErrorContext) -> bool:
        """Determine if the request should be retried."""
        raise NotImplementedError
    
    def get_delay(self, context: ErrorContext) -> float:
        """Get the delay before next retry in seconds."""
        raise NotImplementedError
    
    def get_fallback_action(self, context: ErrorContext) -> Optional[str]:
        """Get fallback action if retries are exhausted."""
        return None


class ExponentialBackoffStrategy(RetryStrategy):
    """Exponential backoff with jitter for retry delays."""
    
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        max_attempts: int = 3,
        jitter: bool = True
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.jitter = jitter
    
    def should_retry(self, context: ErrorContext) -> bool:
        """Retry for transient errors only."""
        if context.attempt_number >= self.max_attempts:
            return False
        
        # Retry for transient errors
        retryable_errors = {
            ErrorType.RATE_LIMIT,
            ErrorType.TIMEOUT,
            ErrorType.NETWORK_ERROR,
            ErrorType.SERVICE_UNAVAILABLE
        }
        
        return context.error_type in retryable_errors
    
    def get_delay(self, context: ErrorContext) -> float:
        """Calculate exponential backoff delay with optional jitter."""
        # Special handling for rate limits
        if context.error_type == ErrorType.RATE_LIMIT and 'retry_after' in context.metadata:
            return float(context.metadata['retry_after'])
        
        # Calculate exponential delay
        delay = min(
            self.base_delay * (2 ** (context.attempt_number - 1)),
            self.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            delay *= (0.5 + random.random())
        
        return delay


class AdaptiveRetryStrategy(RetryStrategy):
    """Adaptive retry strategy that learns from error patterns."""
    
    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts
        self.error_history: List[ErrorContext] = []
        self.success_rate: Dict[str, float] = {}
    
    def should_retry(self, context: ErrorContext) -> bool:
        """Adaptively decide whether to retry based on error patterns."""
        if context.attempt_number >= self.max_attempts:
            return False
        
        # Always retry authentication errors once
        if context.error_type == ErrorType.AUTHENTICATION and context.attempt_number == 1:
            return True
        
        # Don't retry invalid requests
        if context.error_type == ErrorType.INVALID_REQUEST:
            return False
        
        # Check success rate for this provider
        provider_key = f"{context.provider}:{context.model or 'default'}"
        success_rate = self.success_rate.get(provider_key, 1.0)
        
        # Reduce retry attempts for consistently failing providers
        adjusted_max_attempts = max(
            1,
            int(self.max_attempts * success_rate)
        )
        
        return context.attempt_number < adjusted_max_attempts
    
    def get_delay(self, context: ErrorContext) -> float:
        """Get adaptive delay based on error type and history."""
        base_delays = {
            ErrorType.RATE_LIMIT: 10.0,
            ErrorType.TIMEOUT: 2.0,
            ErrorType.API_ERROR: 5.0,
            ErrorType.NETWORK_ERROR: 1.0,
            ErrorType.SERVICE_UNAVAILABLE: 15.0,
            ErrorType.AUTHENTICATION: 0.5,
            ErrorType.UNKNOWN: 3.0
        }
        
        base_delay = base_delays.get(context.error_type, 3.0)
        
        # Increase delay if we've seen many recent errors
        recent_errors = [
            e for e in self.error_history[-10:]
            if (context.timestamp - e.timestamp).total_seconds() < 300  # 5 minutes
        ]
        
        if len(recent_errors) > 5:
            base_delay *= 2.0
        
        # Add jitter
        return base_delay * (0.75 + random.random() * 0.5)
    
    def record_outcome(self, context: ErrorContext, success: bool):
        """Record the outcome of a request for adaptive learning."""
        self.error_history.append(context)
        
        # Keep only recent history
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        # Update success rate
        provider_key = f"{context.provider}:{context.model or 'default'}"
        current_rate = self.success_rate.get(provider_key, 1.0)
        
        # Exponential moving average
        alpha = 0.1
        new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
        self.success_rate[provider_key] = new_rate


class AIErrorHandler:
    """
    Comprehensive error handler for AI operations.
    
    Features:
    - Intelligent retry strategies
    - Error classification
    - Graceful degradation
    - Circuit breaker pattern
    - Detailed error tracking
    """
    
    def __init__(
        self,
        retry_strategy: Optional[RetryStrategy] = None,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        self.retry_strategy = retry_strategy or ExponentialBackoffStrategy()
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # Circuit breaker state
        self._circuit_breakers: Dict[str, datetime] = {}
        self._failure_counts: Dict[str, int] = {}
        
        # Error tracking
        self._error_log: List[ErrorContext] = []
        self._error_stats: Dict[str, int] = {}
    
    def classify_error(self, exception: Exception, provider: str) -> ErrorContext:
        """Classify an exception into an error context."""
        error_message = str(exception)
        error_type = ErrorType.UNKNOWN
        metadata = {}
        
        # Common error patterns
        if "rate limit" in error_message.lower():
            error_type = ErrorType.RATE_LIMIT
            # Try to extract retry-after header
            if hasattr(exception, 'response') and hasattr(exception.response, 'headers'):
                retry_after = exception.response.headers.get('Retry-After')
                if retry_after:
                    metadata['retry_after'] = retry_after
        
        elif "timeout" in error_message.lower() or isinstance(exception, asyncio.TimeoutError):
            error_type = ErrorType.TIMEOUT
        
        elif "unauthorized" in error_message.lower() or "authentication" in error_message.lower():
            error_type = ErrorType.AUTHENTICATION
        
        elif "invalid" in error_message.lower() or "bad request" in error_message.lower():
            error_type = ErrorType.INVALID_REQUEST
        
        elif any(term in error_message.lower() for term in ["connection", "network", "dns"]):
            error_type = ErrorType.NETWORK_ERROR
        
        elif "service unavailable" in error_message.lower() or "503" in error_message:
            error_type = ErrorType.SERVICE_UNAVAILABLE
        
        elif any(term in error_message.lower() for term in ["api", "500", "internal server"]):
            error_type = ErrorType.API_ERROR
        
        return ErrorContext(
            error_type=error_type,
            error_message=error_message,
            provider=provider,
            original_exception=exception,
            metadata=metadata
        )
    
    async def handle_with_retry(
        self,
        func: Callable[..., T],
        *args,
        provider: str,
        model: Optional[str] = None,
        **kwargs
    ) -> T:
        """Execute a function with error handling and retry logic."""
        attempt = 0
        last_error = None
        
        # Check circuit breaker
        if self._is_circuit_open(provider):
            raise Exception(f"Circuit breaker open for {provider}")
        
        while True:
            attempt += 1
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Reset failure count on success
                self._reset_failures(provider)
                
                # Record success if using adaptive strategy
                if isinstance(self.retry_strategy, AdaptiveRetryStrategy) and last_error:
                    self.retry_strategy.record_outcome(last_error, success=True)
                
                return result
                
            except Exception as e:
                # Classify the error
                context = self.classify_error(e, provider)
                context.attempt_number = attempt
                context.model = model
                
                # Log the error
                self._log_error(context)
                last_error = context
                
                # Check if we should retry
                if not self.retry_strategy.should_retry(context):
                    # Record failure if using adaptive strategy
                    if isinstance(self.retry_strategy, AdaptiveRetryStrategy):
                        self.retry_strategy.record_outcome(context, success=False)
                    
                    # Update circuit breaker
                    self._record_failure(provider)
                    
                    # Try fallback or raise
                    fallback = self.retry_strategy.get_fallback_action(context)
                    if fallback:
                        logger.info(f"Using fallback action: {fallback}")
                        # Implement fallback logic here
                    
                    raise e
                
                # Calculate delay
                delay = self.retry_strategy.get_delay(context)
                logger.warning(
                    f"Retrying {provider} after {delay:.1f}s "
                    f"(attempt {attempt}, error: {context.error_type.value})"
                )
                
                # Wait before retry
                await asyncio.sleep(delay)
    
    def handle_with_retry_sync(
        self,
        func: Callable[..., T],
        *args,
        provider: str,
        model: Optional[str] = None,
        **kwargs
    ) -> T:
        """Handle function execution with retry logic synchronously."""
        attempt = 0
        last_error = None
        
        # Check circuit breaker
        if self._is_circuit_open(provider):
            raise Exception(f"Circuit breaker open for {provider}")
        
        while True:
            attempt += 1
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Reset failure count on success
                self._reset_failures(provider)
                
                # Record success if using adaptive strategy
                if isinstance(self.retry_strategy, AdaptiveRetryStrategy) and last_error:
                    self.retry_strategy.record_outcome(last_error, success=True)
                
                return result
                
            except Exception as e:
                # Classify the error
                context = self.classify_error(e, provider)
                context.attempt_number = attempt
                context.model = model
                
                # Log the error
                self._log_error(context)
                last_error = context
                
                # Check if we should retry
                if not self.retry_strategy.should_retry(context):
                    # Record failure if using adaptive strategy
                    if isinstance(self.retry_strategy, AdaptiveRetryStrategy):
                        self.retry_strategy.record_outcome(context, success=False)
                    
                    # Update circuit breaker
                    self._record_failure(provider)
                    
                    raise e
                
                # Calculate delay
                delay = self.retry_strategy.get_delay(context)
                logger.warning(
                    f"Retrying {provider} after {delay:.1f}s "
                    f"(attempt {attempt}, error: {context.error_type.value})"
                )
                
                # Wait before retry
                time.sleep(delay)
    
    def _is_circuit_open(self, provider: str) -> bool:
        """Check if circuit breaker is open for a provider."""
        if provider not in self._circuit_breakers:
            return False
        
        open_time = self._circuit_breakers[provider]
        if (datetime.now() - open_time).total_seconds() > self.circuit_breaker_timeout:
            # Circuit breaker timeout expired, close it
            del self._circuit_breakers[provider]
            self._failure_counts[provider] = 0
            logger.info(f"Circuit breaker closed for {provider}")
            return False
        
        return True
    
    def _record_failure(self, provider: str):
        """Record a failure for circuit breaker."""
        self._failure_counts[provider] = self._failure_counts.get(provider, 0) + 1
        
        if self._failure_counts[provider] >= self.circuit_breaker_threshold:
            self._circuit_breakers[provider] = datetime.now()
            logger.warning(f"Circuit breaker opened for {provider}")
    
    def _reset_failures(self, provider: str):
        """Reset failure count for a provider."""
        self._failure_counts[provider] = 0
        if provider in self._circuit_breakers:
            del self._circuit_breakers[provider]
    
    def _log_error(self, context: ErrorContext):
        """Log an error for tracking."""
        self._error_log.append(context)
        
        # Keep only recent errors
        if len(self._error_log) > 1000:
            self._error_log = self._error_log[-1000:]
        
        # Update statistics
        error_key = f"{context.provider}:{context.error_type.value}"
        self._error_stats[error_key] = self._error_stats.get(error_key, 0) + 1
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            'total_errors': len(self._error_log),
            'error_types': self._error_stats,
            'circuit_breakers': {
                provider: (datetime.now() - open_time).total_seconds()
                for provider, open_time in self._circuit_breakers.items()
            },
            'failure_counts': self._failure_counts
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorContext]:
        """Get recent errors for debugging."""
        return self._error_log[-limit:]