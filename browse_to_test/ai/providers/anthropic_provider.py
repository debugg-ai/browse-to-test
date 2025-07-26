"""
Anthropic (Claude) provider implementation.
"""

import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from ..base import AIProvider, AIResponse, AIProviderError


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider for generating test code."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Anthropic provider."""
        super().__init__(api_key=api_key, **kwargs)
        
        # Set configuration attributes
        self.model = kwargs.get('model', 'claude-3-sonnet-20240229')
        self.temperature = kwargs.get('temperature', 0.1)
        self.max_tokens = kwargs.get('max_tokens', 4000)
        self.timeout = kwargs.get('timeout', 30)
        self.retry_attempts = kwargs.get('retry_attempts', 3)
        self.extra_params = {k: v for k, v in kwargs.items() 
                           if k not in ['model', 'temperature', 'max_tokens', 'timeout', 'retry_attempts']}
        
        # Import Anthropic here to avoid dependency issues
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            raise AIProviderError(
                "Anthropic package not installed. Please install with: pip install anthropic",
                provider="anthropic"
            )
        
        # Set up the client
        if self.api_key:
            self.client = self.anthropic.Anthropic(
                api_key=self.api_key,
                timeout=self.timeout
            )
            # Set up async client
            self.async_client = self.anthropic.AsyncAnthropic(
                api_key=self.api_key,
                timeout=self.timeout
            )
        else:
            # Let Anthropic SDK find the API key from environment
            self.client = self.anthropic.Anthropic(
                timeout=self.timeout
            )
            self.async_client = self.anthropic.AsyncAnthropic(
                timeout=self.timeout
            )
    
    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "anthropic"
    
    @property
    def supported_models(self) -> List[str]:
        """Return list of supported models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        ]
    
    def validate_config(self) -> List[str]:
        """Validate the provider configuration."""
        errors = []
        
        # Check if API key is available
        if not self.api_key:
            import os
            if not os.getenv("ANTHROPIC_API_KEY"):
                errors.append("Anthropic API key not provided and ANTHROPIC_API_KEY environment variable not set")
        
        # Validate model
        if self.model not in self.supported_models:
            errors.append(f"Model '{self.model}' not supported. Supported models: {', '.join(self.supported_models)}")
        
        # Validate parameters
        if self.temperature < 0 or self.temperature > 1:
            errors.append("Temperature must be between 0 and 1 for Anthropic")
        
        if self.max_tokens <= 0:
            errors.append("max_tokens must be positive")
        
        return errors
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate content using Anthropic Claude."""
        start_time = time.time()
        
        # Prepare generation parameters
        generation_params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
            **self.extra_params,
            **kwargs
        }
        
        # Add system prompt if provided
        if system_prompt:
            generation_params["system"] = system_prompt
        
        try:
            response = self._make_request_with_retry(
                self.client.messages.create,
                **generation_params
            )
            
            end_time = time.time()
            
            # Extract response data
            content = ""
            if response.content:
                # Handle both text and other content types
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        content += content_block.text
                    elif isinstance(content_block, str):
                        content += content_block
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=(response.usage.input_tokens + response.usage.output_tokens) if response.usage else None,
                finish_reason=response.stop_reason,
                metadata={
                    "prompt_tokens": response.usage.input_tokens if response.usage else None,
                    "completion_tokens": response.usage.output_tokens if response.usage else None,
                    "response_time": end_time - start_time,
                    "response_id": response.id,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            # Handle Anthropic-specific errors
            if hasattr(self.anthropic, 'AnthropicError') and isinstance(e, self.anthropic.AnthropicError):
                error_msg = f"Anthropic API error: {e}"
            else:
                error_msg = f"Anthropic request failed: {e}"
            
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
        """Generate content using Anthropic Claude asynchronously."""
        start_time = time.time()
        
        # Prepare generation parameters
        generation_params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
            **self.extra_params,
            **kwargs
        }
        
        # Add system prompt if provided
        if system_prompt:
            generation_params["system"] = system_prompt
        
        try:
            response = await self._make_async_request_with_retry(
                self.async_client.messages.create,
                **generation_params
            )
            
            end_time = time.time()
            
            # Extract response data
            content = ""
            if response.content:
                # Handle both text and other content types
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        content += content_block.text
                    elif isinstance(content_block, str):
                        content += content_block
            
            return AIResponse(
                content=content,
                model=self.model,
                provider=self.provider_name,
                tokens_used=(response.usage.input_tokens + response.usage.output_tokens) if response.usage else None,
                finish_reason=response.stop_reason,
                metadata={
                    "prompt_tokens": response.usage.input_tokens if response.usage else None,
                    "completion_tokens": response.usage.output_tokens if response.usage else None,
                    "response_time": end_time - start_time,
                    "response_id": response.id,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            # Handle Anthropic-specific errors
            if hasattr(self.anthropic, 'AnthropicError') and isinstance(e, self.anthropic.AnthropicError):
                error_msg = f"Anthropic API error: {e}"
            else:
                error_msg = f"Anthropic request failed: {e}"
            
            raise AIProviderError(
                error_msg,
                provider=self.provider_name,
                model=self.model
            ) from e
    
    def is_available(self) -> bool:
        """Check if the Anthropic provider is available."""
        try:
            # Check if we have an API key (either provided or in environment)
            if self.api_key:
                return True
            
            import os
            return bool(os.getenv("ANTHROPIC_API_KEY"))
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
            "api_key_available": bool(self.api_key or os.getenv("ANTHROPIC_API_KEY")),
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