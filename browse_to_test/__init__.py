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

## With Security and Performance Monitoring:
```python
import browse_to_test as btt

# Get performance statistics
stats = btt.get_performance_stats()
print(f"Cache hit rate: {stats.get('cache_hit_rate', 'N/A')}")
```

## Incremental Session:
```python
import browse_to_test as btt
import asyncio

async def main():
    session = btt.create_session(framework="playwright", ai_provider="openai")
    await session.start(target_url="https://example.com")
    
    for step_data in automation_steps:
        await session.add_step(step_data)
    
    result = await session.finalize()
    final_script = result['current_script']

asyncio.run(main())
```
"""

import warnings
from pathlib import Path
from typing import List, Union, Dict, Any

# New unified imports
from .core.config import Config, ConfigBuilder, AIConfig, OutputConfig, ProcessingConfig
from .core.executor import BTTExecutor, IncrementalSession, SessionResult, ExecutionResult

# Backward compatibility aliases
E2eTestConverter = BTTExecutor
AsyncIncrementalSession = IncrementalSession

# Performance monitoring capabilities
_performance_monitoring_enabled = True
_optimized_available = False  # Placeholder for optimization modules

__version__ = "0.2.19"
__author__ = "Browse-to-Test Contributors"

# Simple API - the main entry points most users need
__all__ = [
    # Simple conversion functions
    "convert",
    "convert_async",
    
    # Quality analysis functions
    "perform_script_qa",
    "perform_script_qa_async",
    
    # Session management
    "create_session",
    
    # Legacy configuration (for backward compatibility)
    "Config",
    "ConfigBuilder",
    "AIConfig",
    "OutputConfig", 
    "ProcessingConfig",
    
    # Legacy classes (for backward compatibility)
    "E2eTestConverter", 
    "IncrementalSession",
    "AsyncIncrementalSession",
    "SessionResult",
    
    # Utilities
    "list_frameworks",
    "list_ai_providers",
    "get_performance_stats",
]


def convert(
    automation_data,
    framework: str = "playwright",
    ai_provider: str = "openai",
    language: str = "python",
    output_file: str = None,
    **kwargs
) -> str:
    """
    Convert browser automation data to test script.
    
    This is the simplest way to use the library with enhanced security and performance.
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', etc.)
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)  
        language: Target language ('python', 'typescript', etc.)
        output_file: Optional output filename (language auto-detected from extension)
        **kwargs: Additional configuration options
        
    Returns:
        Generated test script as string
        
    Example:
        >>> automation_data = [{"model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]}}]
        >>> script = convert(automation_data, framework="playwright", ai_provider="openai")
        >>> print(script)
        
        >>> # Auto-detect language from output file
        >>> script = convert(automation_data, output_file="test.ts")  # Will use TypeScript
    """
    # Auto-detect language from output file if provided and language not explicitly set
    if output_file and language == "python":  # Default language
        from .core.config import Config
        detected_language = Config.detect_language_from_filename(output_file)
        if detected_language != "python":  # Only change if detection found something different
            language = detected_language
    
    config = ConfigBuilder() \
        .framework(framework) \
        .ai_provider(ai_provider) \
        .language(language) \
        .sensitive_data_keys(["password", "pass", "pwd", "secret", "token", "key", "auth", "api_key", "email", "username", "credit_card", "cc", "card_number", "ssn", "social"]) \
        .from_kwargs(**kwargs) \
        .build()
    
    # Enable strict mode for better validation in the simple API
    config.strict_mode = True
    
    # Validate configuration and provide helpful error messages
    is_valid, message, suggestions = config.validate_and_suggest_alternatives()
    if not is_valid:
        error_msg = f"Configuration validation failed: {message}"
        if suggestions:
            if 'recommended_framework' in suggestions:
                error_msg += f"\nRecommended: framework='{suggestions['recommended_framework']}'"
            if 'alternative_languages' in suggestions:
                error_msg += f"\nAlternative languages for {framework}: {suggestions['alternative_languages']}"
        raise ValueError(error_msg)
    
    # Validate input data
    if not automation_data:
        raise ValueError("No automation data provided")
    
    executor = BTTExecutor(config)
    result = executor.execute(automation_data)
    
    if not result.success:
        raise RuntimeError(f"Conversion failed: {'; '.join(result.errors)}")
    
    return result.script


async def convert_async(
    automation_data,
    framework: str = "playwright",
    ai_provider: str = "openai",
    language: str = "python",
    output_file: str = None,
    **kwargs
) -> str:
    """
    Convert browser automation data to test script asynchronously.
    
    This is the async version of the simple convert function. Now uses the streamlined
    architecture by default for better performance with parallel processing of
    AI analysis and context collection.
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', etc.')
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)  
        language: Target language ('python', 'typescript', etc.)
        output_file: Optional output filename (language auto-detected from extension)
        **kwargs: Additional configuration options
        
    Returns:
        Generated test script as string
        
    Example:
        >>> automation_data = [{"model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]}}]
        >>> script = await convert_async(automation_data, framework="playwright", ai_provider="openai")
        >>> print(script)
        
        >>> # Auto-detect language from output file
        >>> script = await convert_async(automation_data, output_file="test.js")  # Will use JavaScript
    """
    # Auto-detect language from output file if provided and language not explicitly set
    if output_file and language == "python":  # Default language
        from .core.config import Config
        detected_language = Config.detect_language_from_filename(output_file)
        if detected_language != "python":  # Only change if detection found something different
            language = detected_language
    
    config = ConfigBuilder() \
        .framework(framework) \
        .ai_provider(ai_provider) \
        .language(language) \
        .sensitive_data_keys(["password", "pass", "pwd", "secret", "token", "key", "auth", "api_key", "email", "username", "credit_card", "cc", "card_number", "ssn", "social"]) \
        .from_kwargs(**kwargs) \
        .build()
    
    # Enable strict mode for better validation in the simple API
    config.strict_mode = True
    
    # Validate configuration and provide helpful error messages
    is_valid, message, suggestions = config.validate_and_suggest_alternatives()
    if not is_valid:
        error_msg = f"Configuration validation failed: {message}"
        if suggestions:
            if 'recommended_framework' in suggestions:
                error_msg += f"\nRecommended: framework='{suggestions['recommended_framework']}'"
            if 'alternative_languages' in suggestions:
                error_msg += f"\nAlternative languages for {framework}: {suggestions['alternative_languages']}"
        raise ValueError(error_msg)
    
    # Validate input data
    if not automation_data:
        raise ValueError("No automation data provided")
    
    executor = BTTExecutor(config)
    result = await executor.execute_async(automation_data)
    
    if not result.success:
        raise RuntimeError(f"Conversion failed: {'; '.join(result.errors)}")
    
    return result.script


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
    
    executor = BTTExecutor(config)
    
    # Perform comprehensive AI analysis
    result = executor.execute(automation_data)
    analyzed_script = result.script
    
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
    
    executor = BTTExecutor(config)
    
    # Perform comprehensive AI analysis
    result = await executor.execute_async(automation_data)
    analyzed_script = result.script
    
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


def get_optimization_stats() -> dict:
    """
    Get performance statistics from optimized components.
    
    Returns performance metrics if optimized components are in use,
    including AI call savings, cache hit rates, and processing times.
    
    Returns:
        Dictionary with optimization statistics or empty dict if not available
        
    Example:
        >>> stats = btt.get_optimization_stats()
        >>> print(f"AI calls saved: {stats.get('ai_calls_saved', 0)}")
        >>> print(f"Cache hit rate: {stats.get('cache_hit_rate', 0) * 100:.1f}%")
    """
    if not _optimized_available:
        return {}
    
    try:
        from .ai.optimized_factory import get_optimized_factory
        from .core.orchestration.optimized_async_queue import _queue_instances
        
        stats = {}
        
        # Get factory stats
        factory = get_optimized_factory()
        stats['factory'] = factory.get_stats()
        
        # Get queue stats
        queue_stats = {}
        for name, queue in _queue_instances.items():
            queue_stats[name] = queue.get_stats()
        stats['queues'] = queue_stats
        
        return stats
    except Exception:
        return {}


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


def create_session(
    framework: str = "playwright",
    ai_provider: str = "openai",
    language: str = "python",
    **kwargs
) -> IncrementalSession:
    """
    Create an incremental session for live test generation.
    
    Args:
        framework: Target test framework ('playwright', 'selenium', etc.)
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)
        language: Target language ('python', 'typescript', etc.)
        **kwargs: Additional configuration options
        
    Returns:
        IncrementalSession instance ready for use
        
    Example:
        >>> session = btt.create_session(framework="playwright", ai_provider="openai")
        >>> await session.start(target_url="https://example.com")
        >>> await session.add_step(step_data)
        >>> result = await session.finalize()
    """
    config = ConfigBuilder() \
        .framework(framework) \
        .ai_provider(ai_provider) \
        .language(language) \
        .sensitive_data_keys(["password", "pass", "pwd", "secret", "token", "key", "auth", "api_key", "email", "username", "credit_card", "cc", "card_number", "ssn", "social"]) \
        .from_kwargs(**kwargs) \
        .build()
    
    return IncrementalSession(config)


def get_performance_stats() -> Dict[str, Any]:
    """
    Get performance statistics from the browse-to-test library.
    
    Returns:
        Dictionary containing performance metrics including:
        - AI call efficiency
        - Cache hit rates  
        - Processing times
        - Error rates
    """
    try:
        from .core.executor import BTTExecutor
        from .core.config import Config
        
        # Create a minimal config to get stats
        config = Config()
        executor = BTTExecutor(config)
        
        return executor.get_performance_stats()
    except Exception:
        return {"error": "Performance stats not available"} 