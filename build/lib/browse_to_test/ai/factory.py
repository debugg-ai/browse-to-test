"""
Factory for creating AI provider instances.
"""

import logging
from typing import Dict, List, Type
from .base import AIProvider, AIProviderError
from ..core.configuration.config import AIConfig


logger = logging.getLogger(__name__)


class AIProviderFactory:
    """Factory for creating AI provider instances."""
    
    def __init__(self):
        """Initialize the factory with available providers."""
        self._providers: Dict[str, Type[AIProvider]] = {}
        self._register_default_providers()
    
    def _register_default_providers(self):
        """Register all available default providers."""
        try:
            from .providers.openai_provider import OpenAIProvider
            self.register_provider("openai", OpenAIProvider)
        except ImportError as e:
            logger.warning(f"OpenAI provider not available: {e}")
        
        try:
            from .providers.anthropic_provider import AnthropicProvider
            self.register_provider("anthropic", AnthropicProvider)
        except ImportError as e:
            logger.warning(f"Anthropic provider not available: {e}")
        
        try:
            from .providers.azure_provider import AzureOpenAIProvider
            self.register_provider("azure", AzureOpenAIProvider)
        except ImportError as e:
            logger.warning(f"Azure OpenAI provider not available: {e}")
        
        try:
            from .providers.local_provider import LocalAIProvider
            self.register_provider("local", LocalAIProvider)
        except ImportError as e:
            logger.warning(f"Local AI provider not available: {e}")
    
    def register_provider(self, name: str, provider_class: Type[AIProvider]):
        """
        Register a new AI provider.
        
        Args:
            name: Name to register the provider under
            provider_class: Class that implements AIProvider
        """
        if not issubclass(provider_class, AIProvider):
            raise ValueError(f"Provider class must inherit from AIProvider")
        
        self._providers[name.lower()] = provider_class
        logger.debug(f"Registered AI provider: {name}")
    
    def create_provider(self, config: AIConfig) -> AIProvider:
        """
        Create an AI provider instance from configuration.
        
        Args:
            config: AI configuration containing provider details
            
        Returns:
            Configured AI provider instance
            
        Raises:
            AIProviderError: If provider is not available or configuration is invalid
        """
        provider_name = config.provider.lower()
        
        if provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            raise AIProviderError(
                f"Unknown AI provider: {config.provider}. "
                f"Available providers: {available}"
            )
        
        provider_class = self._providers[provider_name]
        
        try:
            # Create provider instance with configuration
            provider = provider_class(
                api_key=config.api_key,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                retry_attempts=config.retry_attempts,
                api_base_url=config.base_url,
                **config.extra_params
            )
            
            # Validate the configuration
            validation_errors = provider.validate_config()
            if validation_errors:
                raise AIProviderError(
                    f"Provider configuration validation failed: {'; '.join(validation_errors)}",
                    provider=provider_name,
                    model=config.model
                )
            
            logger.info(f"Created AI provider: {provider_name} with model: {config.model}")
            return provider
            
        except Exception as e:
            if isinstance(e, AIProviderError):
                raise
            raise AIProviderError(
                f"Failed to create provider {provider_name}: {e}",
                provider=provider_name,
                model=config.model
            ) from e
    
    def list_available_providers(self) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of available provider names
        """
        return sorted(self._providers.keys())
    
    def get_provider_info(self, provider_name: str) -> Dict[str, any]:
        """
        Get information about a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Dictionary containing provider information
            
        Raises:
            AIProviderError: If provider is not found
        """
        provider_name = provider_name.lower()
        
        if provider_name not in self._providers:
            raise AIProviderError(f"Unknown provider: {provider_name}")
        
        provider_class = self._providers[provider_name]
        
        # Create a temporary instance to get information
        try:
            temp_instance = provider_class(api_key="dummy")
            return {
                "name": temp_instance.provider_name,
                "supported_models": temp_instance.supported_models,
                "class": provider_class.__name__,
                "module": provider_class.__module__,
            }
        except Exception as e:
            logger.warning(f"Could not get info for provider {provider_name}: {e}")
            return {
                "name": provider_name,
                "supported_models": [],
                "class": provider_class.__name__,
                "module": provider_class.__module__,
                "error": str(e)
            }
    
    def validate_provider_config(self, config: AIConfig) -> List[str]:
        """
        Validate a provider configuration without creating the provider.
        
        Args:
            config: AI configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        provider_name = config.provider.lower()
        
        if provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            errors.append(f"Unknown AI provider: {config.provider}. Available: {available}")
            return errors
        
        # Check if the model is supported
        try:
            provider_info = self.get_provider_info(provider_name)
            supported_models = provider_info.get("supported_models", [])
            if supported_models and config.model not in supported_models:
                errors.append(
                    f"Model '{config.model}' not supported by {provider_name}. "
                    f"Supported models: {', '.join(supported_models)}"
                )
        except Exception as e:
            errors.append(f"Could not validate model for {provider_name}: {e}")
        
        return errors 