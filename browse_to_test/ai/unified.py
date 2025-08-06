#!/usr/bin/env python3
"""
Unified AI module for browse-to-test library.

This module consolidates all AI functionality into a single, clean interface
that eliminates complexity while maintaining all essential features.
"""

import asyncio
import time
import logging
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types of AI analysis that can be performed."""
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    OPTIMIZATION = "optimization"
    CONVERSION = "conversion"
    VALIDATION = "validation"
    CONTEXT_ANALYSIS = "context_analysis"
    INTELLIGENT_ANALYSIS = "intelligent_analysis"


@dataclass
class AIAnalysisRequest:
    """Request for AI analysis of automation data."""
    analysis_type: AnalysisType
    automation_data: List[Dict[str, Any]]
    target_framework: str
    system_context: Optional[Any] = None
    current_action: Optional[Dict[str, Any]] = None
    
    def to_prompt(self) -> str:
        """Generate a prompt based on the analysis type."""
        if self.analysis_type == AnalysisType.CONVERSION:
            return self._generate_conversion_prompt()
        elif self.analysis_type == AnalysisType.OPTIMIZATION:
            return self._generate_optimization_prompt()
        elif self.analysis_type == AnalysisType.VALIDATION:
            return self._generate_validation_prompt()
        elif self.analysis_type == AnalysisType.CONTEXT_ANALYSIS:
            return self._generate_context_analysis_prompt()
        elif self.analysis_type == AnalysisType.INTELLIGENT_ANALYSIS:
            return self._generate_intelligent_analysis_prompt()
        elif self.analysis_type == AnalysisType.COMPREHENSIVE:
            return self._generate_comprehensive_prompt()
        else:
            # Basic fallback
            return self._generate_basic_prompt()
    
    def _generate_conversion_prompt(self) -> str:
        """Generate conversion analysis prompt."""
        return f"""
Analyze the following automation data for {self.target_framework} conversion:

Automation data: {json.dumps(self.automation_data, indent=2)}

Please provide recommendations for converting this automation data to {self.target_framework} test scripts.
Focus on best practices, proper selectors, and reliable test patterns.
"""
    
    def _generate_optimization_prompt(self) -> str:
        """Generate optimization analysis prompt."""
        prompt = f"""
Analyze the following automation step for {self.target_framework} optimization:

Automation data: {json.dumps(self.automation_data, indent=2)}
"""
        if self.current_action:
            prompt += f"\nCurrent action: {json.dumps(self.current_action, indent=2)}"
        
        prompt += f"""

Please analyze this {self.target_framework} test step and provide specific recommendations:

1. **Reliability Assessment**: Rate the reliability of selectors and actions (mention words like "reliable", "unreliable", "brittle", "stable")
2. **Selector Quality**: Evaluate selector strategies (mention "data-testid", "xpath", "class selector", "id selector")
3. **Wait Strategies**: Recommend appropriate wait conditions (mention "wait", "timeout" if needed)
4. **Error Handling**: Suggest error handling improvements (mention "error handling", "exception" if applicable)
5. **Performance**: Identify performance optimizations (mention "slow", "performance" if relevant)
6. **Maintainability**: Suggest maintainability improvements (mention "maintainability", "readable" if applicable)

For {self.target_framework}-specific optimizations, include framework best practices like:
- Playwright: page.locator usage, auto-wait features
- Selenium: WebDriverWait, expected_conditions

Provide concrete, actionable recommendations.
"""
        return prompt
    
    def _generate_validation_prompt(self) -> str:
        """Generate validation analysis prompt."""
        return f"""
Validate the following automation data for {self.target_framework} compatibility:

Automation data: {json.dumps(self.automation_data, indent=2)}

Please validate this automation data for compatibility with {self.target_framework}.
Check for potential issues, incompatible patterns, and provide recommendations.
"""
    
    def _generate_context_analysis_prompt(self) -> str:
        """Generate context analysis prompt."""
        if self.system_context is None:
            return f"""
Analyze the following automation data with system context for {self.target_framework}:

Automation data: {json.dumps(self.automation_data, indent=2)}

No system context available. Please provide basic analysis for existing tests and patterns.
"""
        
        return f"""
Analyze the following automation data with system context for {self.target_framework}:

Automation data: {json.dumps(self.automation_data, indent=2)}

System context available - analyze in relation to existing tests and project patterns.
Focus on consistency with existing test patterns and project structure.
"""
    
    def _generate_intelligent_analysis_prompt(self) -> str:
        """Generate intelligent analysis prompt."""
        if self.system_context is None:
            return f"""
Perform intelligent analysis of automation data for {self.target_framework}:

Automation data: {json.dumps(self.automation_data, indent=2)}

No system context available. Please provide intelligent analysis with general best practices.
"""
        
        return f"""
Perform intelligent analysis of automation data for {self.target_framework}:

Automation data: {json.dumps(self.automation_data, indent=2)}

System context available - provide context-aware intelligent analysis.
Consider existing patterns, project structure, and provide sophisticated recommendations.
"""
    
    def _generate_comprehensive_prompt(self) -> str:
        """Generate comprehensive analysis prompt."""
        return f"""
Perform comprehensive analysis of automation data for {self.target_framework}:

Automation data: {json.dumps(self.automation_data, indent=2)}

Please provide a general analysis covering all aspects of the automation data.
Include recommendations for test structure, selectors, and best practices.
"""
    
    def _generate_basic_prompt(self) -> str:
        """Generate basic analysis prompt."""
        return f"""
Analyze the following automation data for {self.target_framework}:

Automation data: {json.dumps(self.automation_data, indent=2)}

Please provide basic analysis and recommendations.
"""


class AIProviderError(Exception):
    """Exception raised by AI providers for errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model


@dataclass
class AIResponse:
    """Response from an AI provider."""
    
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Base class for AI providers with built-in retry logic."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize AI provider."""
        self.api_key = api_key
        self.model = kwargs.get('model', 'default')
        self.temperature = kwargs.get('temperature', 0.1)
        self.max_tokens = kwargs.get('max_tokens', 4000)
        self.timeout = kwargs.get('timeout', 30)
        self.retry_attempts = kwargs.get('retry_attempts', 3)
        self.base_delay = kwargs.get('base_delay', 1.0)
        # Store additional config parameters for test compatibility
        self.config = {k: v for k, v in kwargs.items() if k not in {
            'model', 'temperature', 'max_tokens', 'timeout', 'retry_attempts', 'base_delay'
        }}
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if an error should trigger a retry."""
        if attempt >= self.retry_attempts:
            return False
        
        error_str = str(error).lower()
        
        # Retry on rate limits, timeouts, and network errors
        retry_conditions = [
            'rate limit' in error_str,
            'timeout' in error_str,
            'connection' in error_str,
            'network' in error_str,
            'service unavailable' in error_str,
            '429' in error_str,  # Rate limit HTTP code
            '502' in error_str,  # Bad gateway
            '503' in error_str,  # Service unavailable
        ]
        
        return any(retry_conditions)
    
    def _get_retry_delay(self, attempt: int) -> float:
        """Get exponential backoff delay."""
        return min(self.base_delay * (2 ** attempt), 30.0)
    
    async def _retry_with_backoff(self, operation, *args, **kwargs):
        """Execute operation with exponential backoff retry."""
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if not self._should_retry(e, attempt):
                    break
                
                if attempt < self.retry_attempts - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"AI request failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
        
        # If we get here, all retries failed
        raise AIProviderError(f"AI request failed after {self.retry_attempts} attempts: {last_error}", self.provider_name, self.model)
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    async def generate_async(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response asynchronously."""
        pass
    
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response synchronously."""
        try:
            # Check if we're already in an async context
            loop = asyncio.get_running_loop()
            # We're in an async context, this should not be called synchronously
            # Create a new thread to run the async function
            import concurrent.futures
            import threading
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.generate_async(prompt, **kwargs))
                return future.result()
                
        except RuntimeError:
            # No event loop running, we can safely use asyncio.run
            return asyncio.run(self.generate_async(prompt, **kwargs))
    
    def analyze_with_context(self, request: AIAnalysisRequest, **kwargs) -> AIResponse:
        """Analyze automation data with context synchronously."""
        prompt = request.to_prompt()
        return self.generate(prompt, **kwargs)
    
    async def analyze_with_context_async(self, request: AIAnalysisRequest, **kwargs) -> AIResponse:
        """Analyze automation data with context asynchronously."""
        prompt = request.to_prompt()
        return await self.generate_async(prompt, **kwargs)


class OpenAIProvider(AIProvider):
    """Simplified OpenAI provider with built-in retry logic."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize OpenAI provider."""
        # Set proper default model for OpenAI if not specified
        if 'model' not in kwargs:
            kwargs['model'] = 'gpt-4o-mini'
        super().__init__(api_key=api_key, **kwargs)
        self.api_base_url = kwargs.get('api_base_url', 'https://api.openai.com/v1')
        
        if not self.api_key:
            import os
            self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise AIProviderError("OpenAI API key is required", "openai")
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def _make_request(self, prompt: str, **kwargs) -> AIResponse:
        """Make actual API request to OpenAI."""
        import aiohttp
        
        start_time = time.time()
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': kwargs.get('model', self.model),
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens)
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f'{self.api_base_url}/chat/completions', 
                                   headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AIProviderError(f"OpenAI API error {response.status}: {error_text}", "openai")
                
                result = await response.json()
                response_time = time.time() - start_time
                
                return AIResponse(
                    content=result['choices'][0]['message']['content'],
                    model=result['model'],
                    provider="openai",
                    tokens_used=result.get('usage', {}).get('total_tokens'),
                    finish_reason=result['choices'][0].get('finish_reason'),
                    response_time=response_time,
                    metadata={'usage': result.get('usage', {})}
                )
    
    async def generate_async(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response with retry logic."""
        return await self._retry_with_backoff(self._make_request, prompt, **kwargs)


class AnthropicProvider(AIProvider):
    """Simplified Anthropic provider with built-in retry logic."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Anthropic provider."""
        super().__init__(api_key=api_key, **kwargs)
        self.api_base_url = kwargs.get('api_base_url', 'https://api.anthropic.com/v1')
        
        if not self.api_key:
            import os
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise AIProviderError("Anthropic API key is required", "anthropic")
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    async def _make_request(self, prompt: str, **kwargs) -> AIResponse:
        """Make actual API request to Anthropic."""
        import aiohttp
        
        start_time = time.time()
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': kwargs.get('model', self.model),
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens)
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f'{self.api_base_url}/messages', 
                                   headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AIProviderError(f"Anthropic API error {response.status}: {error_text}", "anthropic")
                
                result = await response.json()
                response_time = time.time() - start_time
                
                return AIResponse(
                    content=result['content'][0]['text'],
                    model=result['model'],
                    provider="anthropic",
                    tokens_used=result.get('usage', {}).get('output_tokens', 0) + result.get('usage', {}).get('input_tokens', 0),
                    finish_reason=result.get('stop_reason'),
                    response_time=response_time,
                    metadata={'usage': result.get('usage', {})}
                )
    
    async def generate_async(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response with retry logic."""
        return await self._retry_with_backoff(self._make_request, prompt, **kwargs)


class MockProvider(AIProvider):
    """Mock AI provider for testing."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize mock provider."""
        super().__init__(api_key=api_key or "mock-key", **kwargs)
        self.call_count = 0
        
    @property
    def provider_name(self) -> str:
        return "mock"
    
    async def _make_request(self, prompt: str, **kwargs) -> AIResponse:
        """Mock API request."""
        import asyncio
        
        start_time = time.time()
        self.call_count += 1
        
        # Simulate realistic response time
        await asyncio.sleep(0.5 + (self.call_count % 3) * 0.5)  # 0.5 to 2.0 seconds
        response_time = time.time() - start_time
        
        return AIResponse(
            content=f"Mock response {self.call_count} to: {prompt[:50]}...",
            model="mock-model",
            provider="mock",
            tokens_used=100,
            response_time=response_time
        )
    
    async def generate_async(self, prompt: str, **kwargs) -> AIResponse:
        """Generate mock response."""
        return await self._make_request(prompt, **kwargs)


class AIProviderFactory:
    """Simplified factory for creating AI providers."""
    
    def __init__(self):
        """Initialize the factory with available providers."""
        self._providers = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'mock': MockProvider  # For testing
        }
    
    def create_provider(self, config) -> AIProvider:
        """Create an AI provider instance from configuration."""
        provider_name = getattr(config, 'ai_provider', 'openai').lower()
        
        if provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            raise AIProviderError(f"Unknown AI provider '{provider_name}'. Available: {available}")
        
        provider_class = self._providers[provider_name]
        
        # Extract provider configuration
        provider_kwargs = {
            'api_key': getattr(config, 'api_key', None),
            'model': getattr(config, 'ai_model', None),
            'temperature': getattr(config, 'ai_temperature', 0.1),
            'max_tokens': getattr(config, 'ai_max_tokens', 4000),
            'timeout': getattr(config, 'ai_timeout', 30),
            'retry_attempts': getattr(config, 'ai_retry_attempts', 3),
            'base_url': getattr(config, 'ai_base_url', None),
        }
        
        # Filter out None values
        provider_kwargs = {k: v for k, v in provider_kwargs.items() if v is not None}
        
        return provider_class(**provider_kwargs)
    
    def validate_provider_config(self, config) -> List[str]:
        """Validate provider configuration and return list of errors."""
        errors = []
        
        # Check provider name
        provider_name = getattr(config, 'provider', '') or getattr(config, 'ai_provider', '')
        if not provider_name:
            errors.append("Provider name is required")
        elif provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            errors.append(f"Unknown provider '{provider_name}'. Available: {available}")
        
        # Check API key
        api_key = getattr(config, 'api_key', '')
        if not api_key:
            errors.append("API key is required")
        
        return errors
    
    def list_available_providers(self) -> List[str]:
        """List all available AI providers."""
        return list(self._providers.keys())


# Optimized prompts for common operations
CONVERSION_PROMPT = """Convert these browser actions to {framework} test code:

{actions}

Requirements:
- Use proper selectors and waits
- Include error handling and assertions  
- Generate clean, maintainable code
- Follow {framework} best practices

Output only the test code:"""

OPTIMIZATION_PROMPT = """Optimize this {framework} test action:

Current: {action}
Issues: {issues}

Provide:
1. Improved selector strategy
2. Better wait conditions
3. More reliable approach

Keep response concise:"""


def get_optimized_prompt(template_type: str, **kwargs) -> str:
    """Get an optimized prompt template."""
    if template_type == "conversion":
        return CONVERSION_PROMPT.format(**kwargs)
    elif template_type == "optimization":
        return OPTIMIZATION_PROMPT.format(**kwargs)
    else:
        raise ValueError(f"Unknown prompt template: {template_type}")