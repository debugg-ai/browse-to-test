"""
OpenAI provider implementation.
"""

import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from ..base import AIProvider, AIResponse, AIProviderError


class OpenAIProvider(AIProvider):
    """OpenAI API provider for generating test code."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize OpenAI provider."""
        super().__init__(api_key=api_key, **kwargs)
        
        # Set configuration attributes
        self.model = kwargs.get('model', 'gpt-4')
        self.temperature = kwargs.get('temperature', 0.1)
        self.max_tokens = kwargs.get('max_tokens', 4000)
        self.timeout = kwargs.get('timeout', 30)
        self.retry_attempts = kwargs.get('retry_attempts', 3)
        self.api_base_url = kwargs.get('api_base_url', 'https://api.openai.com/v1')
        self.extra_params = {k: v for k, v in kwargs.items() 
                           if k not in ['model', 'temperature', 'max_tokens', 'timeout', 'retry_attempts', 'api_base_url']}
        
        # Import OpenAI here to avoid dependency issues
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise AIProviderError(
                "OpenAI package not installed. Please install with: pip install openai",
                provider="openai"
            )
        
        # Set up the client
        if self.api_key:
            self.client = self.openai.OpenAI(
                api_key=self.api_key,
                base_url=kwargs.get('api_base_url'),
                timeout=self.timeout
            )
            # Set up async client
            self.async_client = self.openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=kwargs.get('api_base_url'),
                timeout=self.timeout
            )
        else:
            # Let OpenAI SDK find the API key from environment
            self.client = self.openai.OpenAI(
                base_url=kwargs.get('api_base_url'),
                timeout=self.timeout
            )
            self.async_client = self.openai.AsyncOpenAI(
                base_url=kwargs.get('api_base_url'),
                timeout=self.timeout
            )
    
    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "openai"
    
    @property
    def supported_models(self) -> List[str]:
        """Return list of supported models."""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ]
    
    def validate_config(self) -> List[str]:
        """Validate the provider configuration."""
        errors = []
        
        # Check if API key is available (either provided or in environment)
        if not self.api_key:
            import os
            if not os.getenv("OPENAI_API_KEY"):
                errors.append("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        # Validate model
        if self.model not in self.supported_models:
            errors.append(f"Model '{self.model}' not supported. Supported models: {', '.join(self.supported_models)}")
        
        # Validate parameters
        if self.temperature < 0 or self.temperature > 2:
            errors.append("Temperature must be between 0 and 2")
        
        if self.max_tokens <= 0:
            errors.append("max_tokens must be positive")
        
        return errors
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate content using OpenAI."""
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Merge any additional parameters
        generation_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs
        }
        
        try:
            response = self._make_request_with_retry(
                self.client.chat.completions.create,
                **generation_params
            )
            
            end_time = time.time()
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=usage.total_tokens if usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "prompt_tokens": usage.prompt_tokens if usage else None,
                    "completion_tokens": usage.completion_tokens if usage else None,
                    "response_time": end_time - start_time,
                    "response_id": response.id,
                    "created": response.created,
                }
            )
            
        except Exception as e:
            # Handle OpenAI-specific errors
            if hasattr(self.openai, 'OpenAIError') and isinstance(e, self.openai.OpenAIError):
                if hasattr(e, 'code'):
                    error_msg = f"OpenAI API error ({e.code}): {e}"
                else:
                    error_msg = f"OpenAI API error: {e}"
            else:
                error_msg = f"OpenAI request failed: {e}"
            
            raise AIProviderError(
                error_msg,
                provider=self.provider_name,
                model=self.model
            ) from e
    
    async def generate_async(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate content using OpenAI asynchronously."""
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Merge any additional parameters
        generation_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra_params,
            **kwargs
        }
        
        try:
            response = await self._make_async_request_with_retry(
                self.async_client.chat.completions.create,
                **generation_params
            )
            
            end_time = time.time()
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=usage.total_tokens if usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "prompt_tokens": usage.prompt_tokens if usage else None,
                    "completion_tokens": usage.completion_tokens if usage else None,
                    "response_time": end_time - start_time,
                    "response_id": response.id,
                    "created": response.created,
                }
            )
            
        except Exception as e:
            # Handle OpenAI-specific errors
            if hasattr(self.openai, 'OpenAIError') and isinstance(e, self.openai.OpenAIError):
                if hasattr(e, 'code'):
                    error_msg = f"OpenAI API error ({e.code}): {e}"
                else:
                    error_msg = f"OpenAI API error: {e}"
            else:
                error_msg = f"OpenAI request failed: {e}"
            
            raise AIProviderError(
                error_msg,
                provider=self.provider_name,
                model=self.model
            ) from e
    
    def is_available(self) -> bool:
        """Check if the OpenAI provider is available."""
        try:
            # Check if we have an API key (either provided or in environment)
            if self.api_key:
                return True
            
            import os
            return bool(os.getenv("OPENAI_API_KEY"))
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        import os
        return {
            "name": self.model,
            "provider": self.provider_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "supported_models": self.supported_models,
            "api_key_available": bool(self.api_key or os.getenv("OPENAI_API_KEY")),
        }
    
    def _make_request_with_retry(self, request_func, **kwargs):
        """Make request with retry logic."""
        import time
        
        for attempt in range(self.retry_attempts):
            try:
                return request_func(**kwargs)
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise
                
                # Wait before retrying
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
    
    async def _make_async_request_with_retry(self, request_func, **kwargs):
        """Make async request with retry logic."""
        
        for attempt in range(self.retry_attempts):
            try:
                return await request_func(**kwargs)
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise
                
                # Wait before retrying
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)