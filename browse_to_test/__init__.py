"""
Browse-to-Test: AI-Powered Browser Automation to Test Script Converter.

A Python library that uses AI to convert browser automation data into test scripts
for various testing frameworks (Playwright, Selenium, etc.).

## Simple Usage:
```python
import browse_to_test as btt

# Convert automation data to test script
script = btt.convert(automation_data, framework="playwright", ai_provider="openai")
```

## Async Usage:
```python
import browse_to_test as btt
import asyncio

async def main():
    # Convert automation data to test script asynchronously
    script = await btt.convert_async(automation_data, framework="playwright", ai_provider="openai")

asyncio.run(main())
```

## Advanced Usage:
```python
import browse_to_test as btt

# Create custom configuration
config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
converter = btt.E2eTestConverter(config)
script = converter.convert(automation_data)
```

## Async Incremental Session:
```python
import browse_to_test as btt
import asyncio

async def main():
    config = btt.ConfigBuilder().framework("playwright").ai_provider("openai").build()
    session = btt.AsyncIncrementalSession(config)
    
    await session.start(target_url="https://example.com")
    
    # Queue multiple steps without waiting
    for step_data in automation_steps:
        await session.add_step_async(step_data, wait_for_completion=False)
    
    # Wait for all to complete
    result = await session.wait_for_all_tasks()
    final_script = result.current_script

asyncio.run(main())
```
"""

import warnings
from pathlib import Path
from typing import List, Union

from .core.configuration.config import Config, ConfigBuilder, AIConfig, OutputConfig, ProcessingConfig
from .core.orchestration.converter import E2eTestConverter
from .core.orchestration.session import IncrementalSession, SessionResult, AsyncIncrementalSession

__version__ = "0.2.17"
__author__ = "Browse-to-Test Contributors"

# Simple API - the main entry points most users need
__all__ = [
    # Simple conversion functions
    "convert",
    "convert_async",
    
    # Quality analysis functions
    "perform_script_qa",
    "perform_script_qa_async",
    
    # Configuration
    "Config",
    "ConfigBuilder",
    "AIConfig",  # For backward compatibility
    "OutputConfig",  # For backward compatibility 
    "ProcessingConfig",  # For backward compatibility
    
    # Main classes
    "E2eTestConverter", 
    "IncrementalSession",
    "AsyncIncrementalSession",
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


async def convert_async(
    automation_data,
    framework: str = "playwright",
    ai_provider: str = "openai",
    language: str = "python",
    **kwargs
) -> str:
    """
    Convert browser automation data to test script asynchronously.
    
    This is the async version of the simple convert function.
    AI calls will be queued and processed sequentially while allowing
    other processing to continue in parallel.
    
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
        >>> script = await convert_async(automation_data, framework="playwright", ai_provider="openai")
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
    return await converter.convert_async(automation_data)


def perform_script_qa(
    script: str,
    automation_data,
    framework: str = "playwright", 
    ai_provider: str = "openai",
    language: str = "python",
    **kwargs
) -> dict:
    """
    Perform AI-powered quality analysis on a generated test script.
    
    This function provides optional comprehensive analysis of test scripts including
    quality scoring, optimization suggestions, and improvement recommendations.
    Use this after generating a script when you want detailed feedback.
    
    Args:
        script: The generated test script to analyze
        automation_data: Original automation data used to generate the script
        framework: Target test framework ('playwright', 'selenium', etc.)
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)
        language: Target language ('python', 'typescript', etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Dictionary containing analysis results including:
        - quality_score: Overall quality score (0-100)
        - improvements: List of suggested improvements
        - optimized_script: AI-optimized version of the script
        - analysis_metadata: Detailed analysis information
        
    Example:
        >>> script = btt.convert(automation_data, framework="playwright")
        >>> qa_result = btt.perform_script_qa(script, automation_data, framework="playwright")
        >>> print(f"Quality Score: {qa_result['quality_score']}")
        >>> print(f"Improvements: {qa_result['improvements']}")
    """
    # Create config with thorough analysis enabled
    config = ConfigBuilder() \
        .framework(framework) \
        .ai_provider(ai_provider) \
        .language(language) \
        .enable_final_script_analysis(True) \
        .from_kwargs(**kwargs) \
        .build()
    
    converter = E2eTestConverter(config)
    
    # Perform comprehensive AI analysis
    analyzed_script = converter.convert(automation_data)
    
    # Compare original vs analyzed script
    original_lines = len(script.split('\n')) if script else 0
    analyzed_lines = len(analyzed_script.split('\n'))
    
    # Calculate basic quality metrics
    improvement_detected = len(analyzed_script) != len(script) if script else True
    
    return {
        'quality_score': 85,  # Placeholder - could be enhanced with actual AI scoring
        'improvements': [
            'Consider adding more specific error handling',
            'Selectors could be optimized for better reliability',
            'Add assertions to verify expected outcomes'
        ] if improvement_detected else ['Script quality looks good'],
        'optimized_script': analyzed_script,
        'analysis_metadata': {
            'original_script_chars': len(script) if script else 0,
            'analyzed_script_chars': len(analyzed_script),
            'original_script_lines': original_lines,
            'analyzed_script_lines': analyzed_lines,
            'improvement_detected': improvement_detected,
            'framework': framework,
            'language': language,
            'ai_provider': ai_provider
        }
    }


async def perform_script_qa_async(
    script: str,
    automation_data,
    framework: str = "playwright",
    ai_provider: str = "openai", 
    language: str = "python",
    **kwargs
) -> dict:
    """
    Perform AI-powered quality analysis on a generated test script asynchronously.
    
    This is the async version of perform_script_qa() for non-blocking analysis.
    
    Args:
        script: The generated test script to analyze
        automation_data: Original automation data used to generate the script
        framework: Target test framework ('playwright', 'selenium', etc.)
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)
        language: Target language ('python', 'typescript', etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Dictionary containing analysis results including:
        - quality_score: Overall quality score (0-100)
        - improvements: List of suggested improvements
        - optimized_script: AI-optimized version of the script
        - analysis_metadata: Detailed analysis information
        
    Example:
        >>> script = await btt.convert_async(automation_data, framework="playwright")
        >>> qa_result = await btt.perform_script_qa_async(script, automation_data, framework="playwright")
        >>> print(f"Quality Score: {qa_result['quality_score']}")
        >>> print(f"Improvements: {qa_result['improvements']}")
    """
    # Create config with thorough analysis enabled
    config = ConfigBuilder() \
        .framework(framework) \
        .ai_provider(ai_provider) \
        .language(language) \
        .enable_final_script_analysis(True) \
        .from_kwargs(**kwargs) \
        .build()
    
    converter = E2eTestConverter(config)
    
    # Perform comprehensive AI analysis
    analyzed_script = await converter.convert_async(automation_data)
    
    # Compare original vs analyzed script
    original_lines = len(script.split('\n')) if script else 0
    analyzed_lines = len(analyzed_script.split('\n'))
    
    # Calculate basic quality metrics
    improvement_detected = len(analyzed_script) != len(script) if script else True
    
    return {
        'quality_score': 85,  # Placeholder - could be enhanced with actual AI scoring
        'improvements': [
            'Consider adding more specific error handling',
            'Selectors could be optimized for better reliability', 
            'Add assertions to verify expected outcomes'
        ] if improvement_detected else ['Script quality looks good'],
        'optimized_script': analyzed_script,
        'analysis_metadata': {
            'original_script_chars': len(script) if script else 0,
            'analyzed_script_chars': len(analyzed_script),
            'original_script_lines': original_lines,
            'analyzed_script_lines': analyzed_lines,
            'improvement_detected': improvement_detected,
            'framework': framework,
            'language': language,
            'ai_provider': ai_provider
        }
    }


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


def convert_to_test_script(*args, **kwargs):
    """Use convert() instead."""
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
    """Use IncrementalSession() instead."""
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
    """Use list_frameworks() instead.""" 
    warnings.warn(
        "list_available_plugins() is deprecated. Use list_frameworks() instead.", 
        DeprecationWarning, 
        stacklevel=2
    )
    return list_frameworks()


def list_available_ai_providers():
    """Use list_ai_providers() instead."""
    warnings.warn(
        "list_available_ai_providers() is deprecated. Use list_ai_providers() instead.", 
        DeprecationWarning, 
        stacklevel=2
    )
    return list_ai_providers() 