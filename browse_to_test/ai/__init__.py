"""
AI interface layer for the browse-to-test library.

Provides unified, simplified abstractions for different AI providers and models.
"""

from .unified import AIProvider, AIResponse, AIProviderError, OpenAIProvider, AnthropicProvider, get_optimized_prompt
from .factory import AIProviderFactory

# Import from unified module
from .unified import AIAnalysisRequest, AnalysisType

__all__ = [
    "AIProvider",
    "AIResponse", 
    "AIProviderError",
    "AIProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
    "get_optimized_prompt",
    # Backward compatibility
    "AIAnalysisRequest",
    "AnalysisType",
] 