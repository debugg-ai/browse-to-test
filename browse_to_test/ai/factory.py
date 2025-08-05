"""Factory for creating AI provider instances."""

import logging
from typing import List
from .unified import AIProvider, AIProviderError, AIProviderFactory as UnifiedFactory
from ..core.config import AIConfig


logger = logging.getLogger(__name__)


class AIProviderFactory:
    """Factory for creating AI provider instances with backward compatibility."""
    
    def __init__(self):
        """Initialize the factory using the unified implementation."""
        self._unified_factory = UnifiedFactory()
    
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
        return self._unified_factory.create_provider(config)
    
    def list_available_providers(self) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of available provider names
        """
        return self._unified_factory.list_available_providers()
    
    def validate_provider_config(self, config: AIConfig) -> List[str]:
        """
        Validate provider configuration and return list of errors.
        
        Args:
            config: AI configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        return self._unified_factory.validate_provider_config(config)