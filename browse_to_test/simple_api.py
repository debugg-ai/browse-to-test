#!/usr/bin/env python3
"""
Simplified API for browse-to-test library.

This module provides a streamlined developer experience with:
- Preset-based configuration (fast, balanced, accurate, production)
- Smart defaults that work out of the box
- Progressive disclosure of advanced options
- 90% reduction in required configuration
"""

from typing import List, Dict, Any, Optional, Union
from .core.configuration.simple_config import (
    SimpleConfig, SimpleConfigBuilder, ConfigPreset,
    fast_config, balanced_config, accurate_config, production_config
)
from .core.configuration.config_adapter import ConfigAdapter
from .core.orchestration.converter import E2eTestConverter
from .core.orchestration.session import IncrementalSession, SessionResult, AsyncIncrementalSession


# === Simple Conversion Functions ===

def convert_fast(automation_data, 
                framework: str = "playwright", 
                language: str = "python",
                ai_provider: str = "openai") -> str:
    """
    Convert browser automation data to test script using FAST preset.
    
    Optimized for speed (~10 seconds):
    - Uses faster AI models
    - Minimal analysis and context collection
    - Basic error handling
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', 'cypress')
        language: Target language ('python', 'typescript', 'javascript')
        ai_provider: AI provider ('openai', 'anthropic', 'azure')
        
    Returns:
        Generated test script as string
        
    Example:
        >>> script = convert_fast(automation_data, "playwright", "python")
        >>> print(script)
    """
    config = fast_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return converter.convert(automation_data)


def convert_balanced(automation_data,
                    framework: str = "playwright",
                    language: str = "python", 
                    ai_provider: str = "openai") -> str:
    """
    Convert browser automation data to test script using BALANCED preset.
    
    Good balance of speed and quality (~30 seconds):
    - Standard AI models
    - Moderate analysis and context collection
    - Comprehensive error handling
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', 'cypress')
        language: Target language ('python', 'typescript', 'javascript')
        ai_provider: AI provider ('openai', 'anthropic', 'azure')
        
    Returns:
        Generated test script as string
        
    Example:
        >>> script = convert_balanced(automation_data, "selenium", "python")
        >>> print(script)
    """
    config = balanced_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return converter.convert(automation_data)


def convert_accurate(automation_data,
                    framework: str = "playwright",
                    language: str = "python",
                    ai_provider: str = "openai") -> str:
    """
    Convert browser automation data to test script using ACCURATE preset.
    
    Optimized for quality (~90 seconds):
    - Best AI models
    - Deep analysis and comprehensive context collection
    - Full error handling, logging, and screenshots
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', 'cypress')
        language: Target language ('python', 'typescript', 'javascript')
        ai_provider: AI provider ('openai', 'anthropic', 'azure')
        
    Returns:
        Generated test script as string
        
    Example:
        >>> script = convert_accurate(automation_data, "playwright", "typescript")
        >>> print(script)
    """
    config = accurate_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return converter.convert(automation_data)


def convert_production(automation_data,
                      framework: str = "playwright",
                      language: str = "python",
                      ai_provider: str = "openai") -> str:
    """
    Convert browser automation data to test script using PRODUCTION preset.
    
    Production-ready configuration:
    - Robust error handling and logging
    - Sensitive data masking
    - Comprehensive assertions
    - Optimized for reliability
    
    Args:
        automation_data: List of browser automation step dictionaries
        framework: Target test framework ('playwright', 'selenium', 'cypress')
        language: Target language ('python', 'typescript', 'javascript')
        ai_provider: AI provider ('openai', 'anthropic', 'azure')
        
    Returns:
        Generated test script as string
        
    Example:
        >>> script = convert_production(automation_data, "playwright", "python")
        >>> print(script)
    """
    config = production_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return converter.convert(automation_data)


# === Async Versions ===

async def convert_fast_async(automation_data,
                            framework: str = "playwright",
                            language: str = "python",
                            ai_provider: str = "openai") -> str:
    """Async version of convert_fast."""
    config = fast_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return await converter.convert_async(automation_data)


async def convert_balanced_async(automation_data,
                                framework: str = "playwright",
                                language: str = "python",
                                ai_provider: str = "openai") -> str:
    """Async version of convert_balanced."""
    config = balanced_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return await converter.convert_async(automation_data)


async def convert_accurate_async(automation_data,
                                framework: str = "playwright",
                                language: str = "python",
                                ai_provider: str = "openai") -> str:
    """Async version of convert_accurate."""
    config = accurate_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return await converter.convert_async(automation_data)


async def convert_production_async(automation_data,
                                  framework: str = "playwright",
                                  language: str = "python",
                                  ai_provider: str = "openai") -> str:
    """Async version of convert_production."""
    config = production_config(framework, language, ai_provider)
    legacy_config = ConfigAdapter.to_legacy_config(config)
    converter = E2eTestConverter(legacy_config)
    return await converter.convert_async(automation_data)


# === Builder-based API for Custom Configuration ===

def simple_builder() -> SimpleConfigBuilder:
    """
    Create a new SimpleConfigBuilder for custom configuration.
    
    The builder provides a fluent interface for configuration with
    progressive disclosure of advanced options.
    
    Returns:
        SimpleConfigBuilder instance
        
    Example:
        >>> config = simple_builder() \\
        ...     .preset("balanced") \\
        ...     .for_playwright("python") \\
        ...     .with_openai() \\
        ...     .timeout(60) \\
        ...     .build()
        >>> 
        >>> script = convert_with_config(automation_data, config)
    """
    return SimpleConfigBuilder()


def convert_with_config(automation_data, simple_config: SimpleConfig) -> str:
    """
    Convert automation data using a custom SimpleConfig.
    
    Args:
        automation_data: List of browser automation steps
        simple_config: Custom SimpleConfig object
        
    Returns:
        Generated test script as string
    """
    legacy_config = ConfigAdapter.to_legacy_config(simple_config)
    converter = E2eTestConverter(legacy_config)
    return converter.convert(automation_data)


async def convert_with_config_async(automation_data, simple_config: SimpleConfig) -> str:
    """
    Convert automation data using a custom SimpleConfig (async version).
    
    Args:
        automation_data: List of browser automation steps
        simple_config: Custom SimpleConfig object
        
    Returns:
        Generated test script as string
    """
    legacy_config = ConfigAdapter.to_legacy_config(simple_config)
    converter = E2eTestConverter(legacy_config)
    return await converter.convert_async(automation_data)


# === Framework-specific Shortcuts ===

def playwright_python(automation_data, preset: str = "balanced") -> str:
    """Quick conversion for Playwright + Python."""
    return globals()[f"convert_{preset}"](automation_data, "playwright", "python")


def playwright_typescript(automation_data, preset: str = "balanced") -> str:
    """Quick conversion for Playwright + TypeScript."""
    return globals()[f"convert_{preset}"](automation_data, "playwright", "typescript")


def selenium_python(automation_data, preset: str = "balanced") -> str:
    """Quick conversion for Selenium + Python."""
    return globals()[f"convert_{preset}"](automation_data, "selenium", "python")


def cypress_javascript(automation_data, preset: str = "balanced") -> str:
    """Quick conversion for Cypress + JavaScript."""
    return globals()[f"convert_{preset}"](automation_data, "cypress", "javascript")


# === Session Management ===

def start_simple_session(framework: str = "playwright",
                        language: str = "python", 
                        preset: str = "balanced",
                        target_url: Optional[str] = None) -> IncrementalSession:
    """
    Start an incremental session with simplified configuration.
    
    Args:
        framework: Target test framework
        language: Target programming language
        preset: Configuration preset to use
        target_url: Optional target URL to start with
        
    Returns:
        IncrementalSession instance
        
    Example:
        >>> session = start_simple_session("playwright", "python", "fast")
        >>> result = session.start("https://example.com")
        >>> for step in automation_steps:
        ...     session.add_step(step)
        >>> final_script = session.finalize().current_script
    """
    config_func = globals()[f"{preset}_config"]
    simple_config = config_func(framework, language)
    legacy_config = ConfigAdapter.to_legacy_config(simple_config)
    
    session = IncrementalSession(legacy_config)
    if target_url:
        session.start(target_url=target_url)
    
    return session


async def start_simple_session_async(framework: str = "playwright",
                                    language: str = "python",
                                    preset: str = "balanced", 
                                    target_url: Optional[str] = None) -> AsyncIncrementalSession:
    """
    Start an async incremental session with simplified configuration.
    
    Args:
        framework: Target test framework
        language: Target programming language
        preset: Configuration preset to use
        target_url: Optional target URL to start with
        
    Returns:
        AsyncIncrementalSession instance
    """
    config_func = globals()[f"{preset}_config"]
    simple_config = config_func(framework, language)
    legacy_config = ConfigAdapter.to_legacy_config(simple_config)
    
    session = AsyncIncrementalSession(legacy_config)
    if target_url:
        await session.start(target_url=target_url)
    
    return session


# === Utility Functions ===

def compare_presets(automation_data, framework: str = "playwright") -> Dict[str, Any]:
    """
    Compare different presets on the same automation data.
    
    Useful for understanding trade-offs between speed and quality.
    
    Args:
        automation_data: Sample automation data
        framework: Framework to test with
        
    Returns:
        Comparison results with timing and quality metrics
    """
    import time
    
    presets = ["fast", "balanced", "accurate"]
    results = {}
    
    for preset in presets:
        start_time = time.time()
        try:
            script = globals()[f"convert_{preset}"](automation_data, framework)
            duration = time.time() - start_time
            
            results[preset] = {
                "success": True,
                "duration": duration,
                "script_length": len(script.splitlines()),
                "script_size": len(script),
                "estimated_quality": {"fast": 7, "balanced": 8.5, "accurate": 9.5}[preset]
            }
        except Exception as e:
            results[preset] = {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    return results


def suggest_preset(automation_data, requirements: Dict[str, Any] = None) -> str:
    """
    Suggest the best preset based on automation data characteristics and requirements.
    
    Args:
        automation_data: Browser automation data to analyze
        requirements: Optional requirements dict with keys:
                     - max_duration: Maximum acceptable processing time
                     - min_quality: Minimum quality score (1-10)
                     - priority: 'speed', 'quality', or 'balanced'
        
    Returns:
        Recommended preset name
    """
    if not requirements:
        requirements = {}
    
    # Analyze automation data complexity
    step_count = len(automation_data)
    complex_actions = sum(1 for step in automation_data 
                         if any(action in str(step).lower() 
                               for action in ['upload', 'drag', 'complex_selector']))
    
    priority = requirements.get('priority', 'balanced')
    max_duration = requirements.get('max_duration', 60)
    min_quality = requirements.get('min_quality', 7)
    
    # Decision logic
    if priority == 'speed' or max_duration < 20:
        return "fast"
    elif priority == 'quality' or min_quality >= 9:
        return "accurate"
    elif step_count > 20 or complex_actions > 5:
        return "accurate"  # Complex automation needs accurate processing
    else:
        return "balanced"


# === Export all functions ===

__all__ = [
    # Simple conversion functions
    "convert_fast", "convert_balanced", "convert_accurate", "convert_production",
    
    # Async versions
    "convert_fast_async", "convert_balanced_async", "convert_accurate_async", "convert_production_async",
    
    # Builder API
    "simple_builder", "convert_with_config", "convert_with_config_async",
    
    # Framework shortcuts
    "playwright_python", "playwright_typescript", "selenium_python", "cypress_javascript",
    
    # Session management
    "start_simple_session", "start_simple_session_async",
    
    # Utilities
    "compare_presets", "suggest_preset",
    
    # Configuration classes (for advanced users)
    "SimpleConfig", "SimpleConfigBuilder", "ConfigPreset"
]