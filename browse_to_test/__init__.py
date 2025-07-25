"""
Browse-to-Test: AI-Powered Browser Automation to Test Script Converter

A Python library that uses AI to convert browser automation data into test scripts
for various testing frameworks (Playwright, Selenium, etc.).

## Simple Usage:
```python
import browse_to_test as btt

# Convert automation data to test script
script = btt.convert(automation_data, framework="playwright", ai_provider="openai")
```

## Advanced Usage:
```python
import browse_to_test as btt

# Create custom configuration
config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
converter = btt.E2eTestConverter(config)
script = converter.convert(automation_data)
```
"""

from typing import List
from .core.configuration.config import Config, ConfigBuilder, AIConfig, OutputConfig, ProcessingConfig
from .core.orchestration.converter import E2eTestConverter
from .core.orchestration.session import IncrementalSession, SessionResult

__version__ = "0.2.8"
__author__ = "Browse-to-Test Contributors"

# Simple API - the main entry points most users need
__all__ = [
    # Simple conversion function
    "convert",
    
    # Configuration
    "Config",
    "ConfigBuilder",
    "AIConfig",  # For backward compatibility
    "OutputConfig",  # For backward compatibility
    "ProcessingConfig",  # For backward compatibility
    
    # Main classes
    "E2eTestConverter", 
    "IncrementalSession",
    "SessionResult",
    
    # Utilities
    "list_frameworks",
    "list_ai_providers",
]


def convert(
    automation_data,
    framework: str = "playwright",
    ai_provider: str = "openai",
    language: str = "python",
    **kwargs
) -> str:
    """
    Convert browser automation data to test script.
    
    This is the simplest way to use the library.
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', etc.)
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)  
        language: Target language ('python', 'typescript', etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Generated test script as string
        
    Example:
        >>> automation_data = [{"model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]}}]
        >>> script = convert(automation_data, framework="playwright", ai_provider="openai")
        >>> print(script)
    """
    config = ConfigBuilder() \
        .framework(framework) \
        .ai_provider(ai_provider) \
        .language(language) \
        .from_kwargs(**kwargs) \
        .build()
    
    # Enable strict mode for better validation in the simple API
    config.processing.strict_mode = True
    
    converter = E2eTestConverter(config)
    return converter.convert(automation_data)


def list_frameworks() -> List[str]:
    """List all available test frameworks."""
    from .plugins.registry import PluginRegistry
    registry = PluginRegistry()
    return registry.list_available_plugins()


def list_ai_providers() -> List[str]:
    """List all available AI providers."""
    from .ai.factory import AIProviderFactory
    factory = AIProviderFactory()
    return factory.list_available_providers()


# Backward compatibility - keep old API available but mark as deprecated
import warnings
from typing import Union
from pathlib import Path

def convert_to_test_script(*args, **kwargs):
    """Deprecated: Use convert() instead."""
    warnings.warn(
        "convert_to_test_script() is deprecated. Use convert() instead.", 
        DeprecationWarning, 
        stacklevel=2
    )
    return convert(*args, **kwargs)

def start_incremental_session(
    framework: str = "playwright",
    target_url: str = None,
    config: dict = None,
    context_hints: dict = None
):
    """Deprecated: Use IncrementalSession() instead."""
    warnings.warn(
        "start_incremental_session() is deprecated. Use IncrementalSession() instead.", 
        DeprecationWarning, 
        stacklevel=2
    )
    session_config = ConfigBuilder().framework(framework).from_dict(config or {}).build()
    session = IncrementalSession(session_config)
    result = session.start(target_url=target_url, context_hints=context_hints)
    return session, result

# Export deprecated functions for backward compatibility
__all__.extend([
    "convert_to_test_script", 
    "start_incremental_session",
    "list_available_plugins",
    "list_available_ai_providers"
])

def list_available_plugins():
    """Deprecated: Use list_frameworks() instead.""" 
    warnings.warn(
        "list_available_plugins() is deprecated. Use list_frameworks() instead.", 
        DeprecationWarning, 
        stacklevel=2
    )
    return list_frameworks()

def list_available_ai_providers():
    """Deprecated: Use list_ai_providers() instead."""
    warnings.warn(
        "list_available_ai_providers() is deprecated. Use list_ai_providers() instead.", 
        DeprecationWarning, 
        stacklevel=2
    )
    return list_ai_providers() 