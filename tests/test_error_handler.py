#!/usr/bin/env python3
"""
Comprehensive test suite for AIErrorHandler and retry strategies.

This module tests the enhanced error handling system including retry strategies,
circuit breaker patterns, and error classification.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Import the modules under test
from browse_to_test.ai.error_handler import (
    AIErrorHandler,
    ErrorType,
    ErrorContext,
    RetryStrategy,
    ExponentialBackoffStrategy,
    AdaptiveRetryStrategy,
)


class TestErrorType:
    """Test ErrorType enum functionality."""
    
    def test_error_type_values(self):
        """Test all error types have expected values."""
        expected_types = {
            "rate_limit", "timeout", "api_error", "network_error",
            "invalid_request", "authentication", "service_unavailable", "unknown"
        }
        
        actual_types = {error_type.value for error_type in ErrorType}
        assert actual_types == expected_types
    
    def test_error_type_membership(self):
        """Test error type membership checks."""
        assert ErrorType.RATE_LIMIT in ErrorType
        assert ErrorType.TIMEOUT in ErrorType
        assert "invalid_type" not in [t.value for t in ErrorType]


class TestErrorContext:
    """Test ErrorContext functionality."""
    
    def test_basic_creation(self):
        """Test basic ErrorContext creation."""
        context = ErrorContext(
            error_type=ErrorType.RATE_LIMIT,
            error_message="Rate limit exceeded",
            provider="openai"
        )
        
        assert context.error_type == ErrorType.RATE_LIMIT
        assert context.error_message == "Rate limit exceeded"
        assert context.provider == "openai"
        assert context.model is None
        assert isinstance(context.timestamp, datetime)
        assert context.attempt_number == 1
        assert context.original_exception is None
        assert context.metadata == {}
    
    def test_full_creation(self):
        """Test ErrorContext creation with all fields."""
        original_exception = Exception("Original error")
        metadata = {"retry_after": "30", "request_id": "test_123"}
        
        context = ErrorContext(
            error_type=ErrorType.API_ERROR,
            error_message="Internal server error",
            provider="anthropic",
            model="claude-3-sonnet",
            attempt_number=2,
            original_exception=original_exception,
            metadata=metadata
        )
        
        assert context.error_type == ErrorType.API_ERROR
        assert context.error_message == "Internal server error"
        assert context.provider == "anthropic"
        assert context.model == "claude-3-sonnet"
        assert context.attempt_number == 2
        assert context.original_exception == original_exception
        assert context.metadata == metadata


class TestExponentialBackoffStrategy:
    """Test ExponentialBackoffStrategy functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = ExponentialBackoffStrategy(
            base_delay=1.0,
            max_delay=10.0,
            max_attempts=3,
            jitter=False  # Disable jitter for predictable testing
        )
    
    def test_initialization(self):
        """Test strategy initialization."""
        strategy = ExponentialBackoffStrategy(
            base_delay=2.0,
            max_delay=30.0,
            max_attempts=5,
            jitter=True
        )
        
        assert strategy.base_delay == 2.0
        assert strategy.max_delay == 30.0
        assert strategy.max_attempts == 5
        assert strategy.jitter is True
    
    def test_should_retry_transient_errors(self):
        """Test retry decisions for transient errors."""
        retryable_errors = [
            ErrorType.RATE_LIMIT,
            ErrorType.TIMEOUT,
            ErrorType.NETWORK_ERROR,
            ErrorType.SERVICE_UNAVAILABLE
        ]
        
        for error_type in retryable_errors:
            context = ErrorContext(
                error_type=error_type,
                error_message="Test error",
                provider="test_provider",
                attempt_number=1
            )
            assert self.strategy.should_retry(context), f"Should retry {error_type}"
    
    def test_should_not_retry_permanent_errors(self):
        """Test retry decisions for permanent errors."""
        non_retryable_errors = [
            ErrorType.INVALID_REQUEST,
            ErrorType.AUTHENTICATION,
            ErrorType.API_ERROR,
            ErrorType.UNKNOWN
        ]
        
        for error_type in non_retryable_errors:
            context = ErrorContext(
                error_type=error_type,
                error_message="Test error",
                provider="test_provider",
                attempt_number=1
            )
            assert not self.strategy.should_retry(context), f"Should not retry {error_type}"
    
    def test_should_not_retry_max_attempts_reached(self):
        """Test that retry is refused when max attempts reached."""
        context = ErrorContext(
            error_type=ErrorType.RATE_LIMIT,
            error_message="Rate limit",
            provider="test_provider",
            attempt_number=3  # At max attempts
        )
        
        assert not self.strategy.should_retry(context)
    
    def test_exponential_delay_calculation(self):
        """Test exponential backoff delay calculation."""
        contexts = [
            ErrorContext(ErrorType.TIMEOUT, "timeout", "provider", attempt_number=1),
            ErrorContext(ErrorType.TIMEOUT, "timeout", "provider", attempt_number=2),
            ErrorContext(ErrorType.TIMEOUT, "timeout", "provider", attempt_number=3),
        ]
        
        delays = [self.strategy.get_delay(context) for context in contexts]
        
        # Should follow exponential pattern: 1, 2, 4
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
    
    def test_max_delay_capping(self):
        """Test that delay is capped at max_delay."""
        context = ErrorContext(
            error_type=ErrorType.TIMEOUT,
            error_message="timeout",
            provider="provider",
            attempt_number=10  # Would normally result in very large delay
        )
        
        delay = self.strategy.get_delay(context)
        assert delay <= self.strategy.max_delay
    
    def test_rate_limit_retry_after_header(self):
        """Test special handling of rate limit retry-after header."""
        context = ErrorContext(
            error_type=ErrorType.RATE_LIMIT,
            error_message="rate limit",
            provider="provider",
            attempt_number=1,
            metadata={"retry_after": "15"}
        )
        
        delay = self.strategy.get_delay(context)
        assert delay == 15.0
    
    def test_jitter_application(self):
        """Test that jitter is applied when enabled."""
        strategy_with_jitter = ExponentialBackoffStrategy(
            base_delay=1.0,
            max_delay=10.0,
            max_attempts=3,
            jitter=True
        )
        
        context = ErrorContext(
            error_type=ErrorType.TIMEOUT,
            error_message="timeout",
            provider="provider",
            attempt_number=1
        )
        
        # Generate multiple delays to check variance
        delays = [strategy_with_jitter.get_delay(context) for _ in range(10)]
        
        # All delays should be between 0.5 and 1.5 (base_delay * jitter range)
        assert all(0.5 <= delay <= 1.5 for delay in delays)
        
        # There should be some variance (not all identical)
        assert len(set(delays)) > 1


class TestAdaptiveRetryStrategy:
    """Test AdaptiveRetryStrategy functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = AdaptiveRetryStrategy(max_attempts=5)
    
    def test_initialization(self):
        """Test strategy initialization."""
        strategy = AdaptiveRetryStrategy(max_attempts=3)
        
        assert strategy.max_attempts == 3
        assert strategy.error_history == []
        assert strategy.success_rate == {}
    
    def test_should_retry_authentication_once(self):
        """Test that authentication errors are retried once."""
        context = ErrorContext(
            error_type=ErrorType.AUTHENTICATION,
            error_message="Unauthorized",
            provider="openai",
            attempt_number=1
        )
        
        assert self.strategy.should_retry(context)
        
        # Second attempt should not be retried (create new context)
        context2 = ErrorContext(
            error_type=ErrorType.AUTHENTICATION,
            error_message="Unauthorized",
            provider="openai",
            attempt_number=2
        )
        assert not self.strategy.should_retry(context2)
    
    def test_should_not_retry_invalid_requests(self):
        """Test that invalid requests are never retried."""
        context = ErrorContext(
            error_type=ErrorType.INVALID_REQUEST,
            error_message="Bad request",
            provider="openai",
            attempt_number=1
        )
        
        assert not self.strategy.should_retry(context)
    
    def test_adaptive_max_attempts_based_on_success_rate(self):
        """Test that max attempts are adjusted based on provider success rate."""
        provider_key = "openai:gpt-4"
        
        # Set low success rate for provider
        self.strategy.success_rate[provider_key] = 0.3
        
        context = ErrorContext(
            error_type=ErrorType.TIMEOUT,
            error_message="timeout",
            provider="openai",
            model="gpt-4",
            attempt_number=2
        )
        
        # With low success rate, should reduce retry attempts
        # adjusted_max = max(1, int(5 * 0.3)) = max(1, 1) = 1
        # So attempt 2 should not be retried
        assert not self.strategy.should_retry(context)
    
    def test_adaptive_delay_calculation(self):
        """Test adaptive delay calculation based on error type."""
        test_cases = [
            (ErrorType.RATE_LIMIT, 10.0),
            (ErrorType.TIMEOUT, 2.0),
            (ErrorType.API_ERROR, 5.0),
            (ErrorType.NETWORK_ERROR, 1.0),
            (ErrorType.SERVICE_UNAVAILABLE, 15.0),
            (ErrorType.AUTHENTICATION, 0.5),
            (ErrorType.UNKNOWN, 3.0)
        ]
        
        for error_type, expected_base_delay in test_cases:
            context = ErrorContext(
                error_type=error_type,
                error_message="test",
                provider="provider"
            )
            
            delay = self.strategy.get_delay(context)
            
            # Delay should be in expected range (base_delay * jitter range)
            min_delay = expected_base_delay * 0.75
            max_delay = expected_base_delay * 1.25
            assert min_delay <= delay <= max_delay, f"Delay {delay} not in range [{min_delay}, {max_delay}] for {error_type}"
    
    def test_delay_increase_with_recent_errors(self):
        """Test that delay increases when there are many recent errors."""
        # Add many recent errors to history
        now = datetime.now()
        for i in range(8):
            error_context = ErrorContext(
                error_type=ErrorType.API_ERROR,
                error_message=f"error_{i}",
                provider="provider",
                timestamp=now - timedelta(seconds=i)  # Recent errors
            )
            self.strategy.error_history.append(error_context)
        
        context = ErrorContext(
            error_type=ErrorType.TIMEOUT,
            error_message="timeout",
            provider="provider"
        )
        
        delay = self.strategy.get_delay(context)
        
        # Should be double the base delay due to recent errors
        # Base delay for timeout is 2.0, so should be around 4.0 * jitter
        assert 3.0 <= delay <= 5.0
    
    def test_record_outcome_success(self):
        """Test recording successful outcomes."""
        context = ErrorContext(
            error_type=ErrorType.TIMEOUT,
            error_message="timeout",
            provider="openai",
            model="gpt-4"
        )
        
        # Record success
        self.strategy.record_outcome(context, success=True)
        
        # Should update success rate
        provider_key = "openai:gpt-4"
        assert provider_key in self.strategy.success_rate
        # With exponential moving average: 0.1 * 1.0 + 0.9 * 1.0 = 1.0
        assert self.strategy.success_rate[provider_key] == 1.0
        
        # Should add to error history
        assert len(self.strategy.error_history) == 1
    
    def test_record_outcome_failure(self):
        """Test recording failed outcomes."""
        context = ErrorContext(
            error_type=ErrorType.API_ERROR,
            error_message="api error",
            provider="anthropic",
            model="claude-3-sonnet"
        )
        
        # Record failure
        self.strategy.record_outcome(context, success=False)
        
        # Should update success rate
        provider_key = "anthropic:claude-3-sonnet"
        assert provider_key in self.strategy.success_rate
        # With exponential moving average: 0.1 * 0.0 + 0.9 * 1.0 = 0.9
        assert self.strategy.success_rate[provider_key] == 0.9
    
    def test_error_history_size_limit(self):
        """Test that error history is limited in size."""
        # Add more than 100 errors
        for i in range(150):
            context = ErrorContext(
                error_type=ErrorType.TIMEOUT,
                error_message=f"timeout_{i}",
                provider="provider"
            )
            self.strategy.record_outcome(context, success=False)
        
        # Should be limited to 100
        assert len(self.strategy.error_history) == 100


class TestAIErrorHandler:
    """Test AIErrorHandler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.retry_strategy = Mock(spec=RetryStrategy)
        self.error_handler = AIErrorHandler(
            retry_strategy=self.retry_strategy,
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=5.0
        )
    
    def test_initialization_with_default_strategy(self):
        """Test error handler initialization with default strategy."""
        handler = AIErrorHandler()
        
        assert isinstance(handler.retry_strategy, ExponentialBackoffStrategy)
        assert handler.circuit_breaker_threshold == 5
        assert handler.circuit_breaker_timeout == 60.0
        assert handler._circuit_breakers == {}
        assert handler._failure_counts == {}
        assert handler._error_log == []
        assert handler._error_stats == {}
    
    def test_initialization_with_custom_strategy(self):
        """Test error handler initialization with custom strategy."""
        custom_strategy = AdaptiveRetryStrategy(max_attempts=10)
        handler = AIErrorHandler(
            retry_strategy=custom_strategy,
            circuit_breaker_threshold=2,
            circuit_breaker_timeout=30.0
        )
        
        assert handler.retry_strategy == custom_strategy
        assert handler.circuit_breaker_threshold == 2
        assert handler.circuit_breaker_timeout == 30.0
    
    def test_classify_rate_limit_error(self):
        """Test classification of rate limit errors."""
        exception = Exception("Rate limit exceeded. Please try again later.")
        
        context = self.error_handler.classify_error(exception, "openai")
        
        assert context.error_type == ErrorType.RATE_LIMIT
        assert context.error_message == "Rate limit exceeded. Please try again later."
        assert context.provider == "openai"
        assert context.original_exception == exception
    
    def test_classify_timeout_error(self):
        """Test classification of timeout errors."""
        timeout_exception = asyncio.TimeoutError("Request timed out")
        
        context = self.error_handler.classify_error(timeout_exception, "anthropic")
        
        assert context.error_type == ErrorType.TIMEOUT
        assert context.provider == "anthropic"
    
    def test_classify_authentication_error(self):
        """Test classification of authentication errors."""
        auth_exception = Exception("Unauthorized: Invalid API key")
        
        context = self.error_handler.classify_error(auth_exception, "openai")
        
        assert context.error_type == ErrorType.AUTHENTICATION
        assert context.provider == "openai"
    
    def test_classify_network_error(self):
        """Test classification of network errors."""
        network_exception = Exception("Connection failed: DNS resolution error")
        
        context = self.error_handler.classify_error(network_exception, "provider")
        
        assert context.error_type == ErrorType.NETWORK_ERROR
    
    def test_classify_invalid_request_error(self):
        """Test classification of invalid request errors."""
        invalid_exception = Exception("Bad request: Invalid parameters")
        
        context = self.error_handler.classify_error(invalid_exception, "provider")
        
        assert context.error_type == ErrorType.INVALID_REQUEST
    
    def test_classify_service_unavailable_error(self):
        """Test classification of service unavailable errors."""
        service_exception = Exception("Service unavailable (503)")
        
        context = self.error_handler.classify_error(service_exception, "provider")
        
        assert context.error_type == ErrorType.SERVICE_UNAVAILABLE
    
    def test_classify_api_error(self):
        """Test classification of API errors."""
        api_exception = Exception("Internal server error (500)")
        
        context = self.error_handler.classify_error(api_exception, "provider")
        
        assert context.error_type == ErrorType.API_ERROR
    
    def test_classify_unknown_error(self):
        """Test classification of unknown errors."""
        unknown_exception = Exception("Some unexpected error")
        
        context = self.error_handler.classify_error(unknown_exception, "provider")
        
        assert context.error_type == ErrorType.UNKNOWN
    
    def test_classify_rate_limit_with_retry_after_header(self):
        """Test classification of rate limit with retry-after header."""
        # Mock exception with response headers
        exception = Exception("Rate limit exceeded")
        exception.response = Mock()
        exception.response.headers = {"Retry-After": "30"}
        
        context = self.error_handler.classify_error(exception, "openai")
        
        assert context.error_type == ErrorType.RATE_LIMIT
        assert context.metadata["retry_after"] == "30"
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_success_on_first_attempt(self):
        """Test successful execution on first attempt."""
        # Set up mock function
        mock_func = AsyncMock(return_value="success")
        
        # Execute with retry handling
        result = await self.error_handler.handle_with_retry(
            mock_func, "arg1", "arg2", provider="openai", model="gpt-4", kwarg1="value1"
        )
        
        assert result == "success"
        mock_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")
        
        # No retry should have been attempted
        self.retry_strategy.should_retry.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_success_after_retries(self):
        """Test successful execution after retries."""
        # Set up mock function to fail first, then succeed
        mock_func = AsyncMock(side_effect=[
            Exception("Temporary error"),
            "success"
        ])
        
        # Set up retry strategy
        self.retry_strategy.should_retry.return_value = True
        self.retry_strategy.get_delay.return_value = 0.01  # Short delay for testing
        
        # Execute with retry handling
        result = await self.error_handler.handle_with_retry(
            mock_func, provider="openai"
        )
        
        assert result == "success"
        assert mock_func.call_count == 2
        
        # Retry strategy should have been consulted
        self.retry_strategy.should_retry.assert_called_once()
        self.retry_strategy.get_delay.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_exhausted_retries(self):
        """Test behavior when retries are exhausted."""
        # Set up mock function to always fail
        error = Exception("Persistent error")
        mock_func = AsyncMock(side_effect=error)
        
        # Set up retry strategy to refuse retry
        self.retry_strategy.should_retry.return_value = False
        
        # Execute should raise the original exception
        with pytest.raises(Exception, match="Persistent error"):
            await self.error_handler.handle_with_retry(
                mock_func, provider="openai"
            )
        
        mock_func.assert_called_once()
        self.retry_strategy.should_retry.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_circuit_breaker_open(self):
        """Test circuit breaker prevents execution when open."""
        # Open circuit breaker by recording failures
        provider = "failing_provider"
        for _ in range(3):  # Reach threshold
            self.error_handler._record_failure(provider)
        
        mock_func = AsyncMock(return_value="success")
        
        # Should raise circuit breaker exception
        with pytest.raises(Exception, match="Circuit breaker open"):
            await self.error_handler.handle_with_retry(
                mock_func, provider=provider
            )
        
        # Function should not have been called
        mock_func.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_timeout_recovery(self):
        """Test circuit breaker closes after timeout."""
        provider = "test_provider"
        
        # Open circuit breaker
        for _ in range(3):
            self.error_handler._record_failure(provider)
        
        assert self.error_handler._is_circuit_open(provider)
        
        # Manually set circuit breaker time to past
        past_time = datetime.now() - timedelta(seconds=10)
        self.error_handler._circuit_breakers[provider] = past_time
        
        # Circuit breaker should now be closed
        assert not self.error_handler._is_circuit_open(provider)
        
        # Failure count should be reset
        assert self.error_handler._failure_counts[provider] == 0
    
    def test_handle_with_retry_sync_success(self):
        """Test synchronous retry handler success."""
        mock_func = Mock(return_value="sync_success")
        
        result = self.error_handler.handle_with_retry_sync(
            mock_func, "arg1", provider="openai", kwarg1="value1"
        )
        
        assert result == "sync_success"
        mock_func.assert_called_once_with("arg1", kwarg1="value1")
    
    def test_handle_with_retry_sync_with_retries(self):
        """Test synchronous retry handler with retries."""
        # Set up mock function to fail first, then succeed
        mock_func = Mock(side_effect=[
            Exception("Temporary error"),
            "success"
        ])
        
        # Set up retry strategy
        self.retry_strategy.should_retry.return_value = True
        self.retry_strategy.get_delay.return_value = 0.01
        
        # Mock time.sleep to speed up test
        with patch('time.sleep'):
            result = self.error_handler.handle_with_retry_sync(
                mock_func, provider="openai"
            )
        
        assert result == "success"
        assert mock_func.call_count == 2
    
    def test_error_logging_and_statistics(self):
        """Test error logging and statistics tracking."""
        # Create some errors
        errors = [
            (ErrorType.RATE_LIMIT, "openai"),
            (ErrorType.TIMEOUT, "anthropic"),
            (ErrorType.API_ERROR, "openai"),
            (ErrorType.RATE_LIMIT, "openai"),
        ]
        
        for error_type, provider in errors:
            context = ErrorContext(
                error_type=error_type,
                error_message="test error",
                provider=provider
            )
            self.error_handler._log_error(context)
        
        # Check error log
        assert len(self.error_handler._error_log) == 4
        
        # Check statistics
        stats = self.error_handler.get_error_statistics()
        assert stats['total_errors'] == 4
        assert stats['error_types']['openai:rate_limit'] == 2
        assert stats['error_types']['anthropic:timeout'] == 1
        assert stats['error_types']['openai:api_error'] == 1
    
    def test_error_log_size_limit(self):
        """Test that error log size is limited."""
        # Add more than 1000 errors
        for i in range(1200):
            context = ErrorContext(
                error_type=ErrorType.TIMEOUT,
                error_message=f"error_{i}",
                provider="provider"
            )
            self.error_handler._log_error(context)
        
        # Should be limited to 1000
        assert len(self.error_handler._error_log) == 1000
    
    def test_get_recent_errors(self):
        """Test retrieving recent errors."""
        # Add some errors
        for i in range(20):
            context = ErrorContext(
                error_type=ErrorType.TIMEOUT,
                error_message=f"error_{i}",
                provider="provider"
            )
            self.error_handler._log_error(context)
        
        # Get recent errors
        recent_errors = self.error_handler.get_recent_errors(limit=5)
        
        assert len(recent_errors) == 5
        # Should be the most recent ones
        assert recent_errors[-1].error_message == "error_19"
        assert recent_errors[0].error_message == "error_15"
    
    def test_reset_failures_on_success(self):
        """Test that failure count is reset on success."""
        provider = "test_provider"
        
        # Record some failures
        self.error_handler._record_failure(provider)
        self.error_handler._record_failure(provider)
        
        assert self.error_handler._failure_counts[provider] == 2
        
        # Reset on success
        self.error_handler._reset_failures(provider)
        
        assert self.error_handler._failure_counts[provider] == 0
        assert provider not in self.error_handler._circuit_breakers


class TestErrorHandlerIntegration:
    """Test error handler integration with real retry strategies."""
    
    @pytest.mark.asyncio
    async def test_integration_with_exponential_backoff(self):
        """Test integration with exponential backoff strategy."""
        strategy = ExponentialBackoffStrategy(
            base_delay=0.01,  # Short delays for testing
            max_delay=0.1,
            max_attempts=3,
            jitter=False
        )
        
        handler = AIErrorHandler(retry_strategy=strategy)
        
        # Create a function that fails twice then succeeds
        call_count = 0
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Timeout error")  # Will be retried
            elif call_count == 2:
                raise Exception("Network connection failed")  # Will be retried
            return "success"
        
        # Should succeed after retries
        result = await handler.handle_with_retry(
            failing_func, provider="test_provider"
        )
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_integration_with_adaptive_strategy(self):
        """Test integration with adaptive retry strategy."""
        strategy = AdaptiveRetryStrategy(max_attempts=5)
        handler = AIErrorHandler(retry_strategy=strategy)
        
        # Create a function that fails with different error types
        failures = [
            Exception("Authentication error"),  # Should not retry
            Exception("Rate limit exceeded"),   # Should retry
        ]
        
        async def auth_failing_func():
            raise failures[0]
        
        async def rate_limit_failing_func():
            raise failures[1]
        
        # Authentication error should not be retried
        with pytest.raises(Exception, match="Authentication error"):
            await handler.handle_with_retry(
                auth_failing_func, provider="test_provider"
            )
        
        # Rate limit error should be retried (but will keep failing)
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await handler.handle_with_retry(
                rate_limit_failing_func, provider="test_provider"
            )
    
    @pytest.mark.asyncio 
    async def test_adaptive_strategy_learning(self):
        """Test that adaptive strategy learns from outcomes."""
        strategy = AdaptiveRetryStrategy(max_attempts=5)
        handler = AIErrorHandler(retry_strategy=strategy)
        
        provider = "learning_provider"
        model = "test_model"
        
        # Simulate several failures
        async def failing_func():
            raise Exception("API error")
        
        for _ in range(3):
            try:
                await handler.handle_with_retry(
                    failing_func, provider=provider, model=model
                )
            except:
                pass
        
        # Check that success rate has been updated
        provider_key = f"{provider}:{model}"
        assert provider_key in strategy.success_rate
        assert strategy.success_rate[provider_key] < 1.0
        
        # Simulate a success
        async def success_func():
            return "success"
        
        result = await handler.handle_with_retry(
            success_func, provider=provider, model=model
        )
        
        assert result == "success"
        # Success rate should have improved
        assert strategy.success_rate[provider_key] > 0.0


class TestErrorHandlerPerformance:
    """Test error handler performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_retry_timing_accuracy(self):
        """Test that retry delays are approximately correct."""
        strategy = ExponentialBackoffStrategy(
            base_delay=0.1,
            max_delay=1.0,
            max_attempts=3,
            jitter=False
        )
        
        handler = AIErrorHandler(retry_strategy=strategy)
        
        # Function that fails twice then succeeds
        call_times = []
        
        async def timed_failing_func():
            call_times.append(time.time())
            if len(call_times) <= 2:
                raise Exception("Timeout")
            return "success"
        
        start_time = time.time()
        result = await handler.handle_with_retry(
            timed_failing_func, provider="test_provider"
        )
        total_time = time.time() - start_time
        
        assert result == "success"
        assert len(call_times) == 3
        
        # Check timing between calls
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        # Should be approximately 0.1 and 0.2 seconds (with some tolerance)
        assert 0.08 <= delay1 <= 0.12
        assert 0.18 <= delay2 <= 0.22
        
        # Total time should be reasonable
        assert 0.25 <= total_time <= 0.4
    
    def test_error_classification_performance(self):
        """Test error classification performance with many errors."""
        handler = AIErrorHandler()
        
        # Test classification of many errors
        start_time = time.time()
        
        error_messages = [
            "Rate limit exceeded",
            "Request timed out", 
            "Unauthorized access",
            "Invalid request parameters",
            "Network connection failed",
            "Service unavailable",
            "Internal server error",
            "Unknown error occurred"
        ] * 100  # 800 total classifications
        
        for message in error_messages:
            exception = Exception(message)
            context = handler.classify_error(exception, "test_provider")
            assert isinstance(context, ErrorContext)
        
        classification_time = time.time() - start_time
        
        # Should be fast (less than 1 second for 800 classifications)
        assert classification_time < 1.0
        
        # Average time per classification should be reasonable
        avg_time = classification_time / len(error_messages)
        assert avg_time < 0.001  # Less than 1ms per classification