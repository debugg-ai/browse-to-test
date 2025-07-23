"""
AI interface layer for the browse-to-test library.

Provides abstractions for different AI providers and models.
"""

from .base import AIProvider, AIResponse
from .factory import AIProviderFactory
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider

__all__ = [
    "AIProvider",
    "AIResponse", 
    "AIProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
] 