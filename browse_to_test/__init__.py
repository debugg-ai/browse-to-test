"""
Browse-to-Test: AI-Powered Browser Automation to Test Script Converter

A Python library that uses AI to convert browser automation data into test scripts
for various testing frameworks (Playwright, Selenium, etc.).
"""

from .core.orchestrator import TestScriptOrchestrator
from .core.config import Config, AIConfig, OutputConfig
from .plugins.registry import PluginRegistry
from .ai.factory import AIProviderFactory

__version__ = "0.1.0"
__author__ = "Browse-to-Test Contributors"

# Main API exports
__all__ = [
    "TestScriptOrchestrator",
    "Config", 
    "AIConfig",
    "OutputConfig",
    "PluginRegistry",
    "AIProviderFactory",
    "convert_to_test_script",
    "list_available_plugins",
    "list_available_ai_providers",
]

def convert_to_test_script(
    automation_data: list[dict],
    output_framework: str = "playwright",
    ai_provider: str = "openai",
    config: dict = None
) -> str:
    """
    Convert browser automation data to test script.
    
    This is the main convenience function for simple usage.
    
    Args:
        automation_data: List of browser automation step dictionaries
        output_framework: Target test framework ('playwright', 'selenium', etc.)
        ai_provider: AI provider to use ('openai', 'anthropic', etc.)
        config: Optional configuration dictionary
        
    Returns:
        Generated test script as string
        
    Example:
        >>> automation_data = [{"model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]}}]
        >>> script = convert_to_test_script(automation_data, "playwright", "openai")
        >>> print(script)
    """
    from .core.config import Config
    
    # Create configuration
    config_obj = Config.from_dict(config or {})
    config_obj.output.framework = output_framework
    config_obj.ai.provider = ai_provider
    
    # Create orchestrator and generate script
    orchestrator = TestScriptOrchestrator(config_obj)
    return orchestrator.generate_test_script(automation_data)

def list_available_plugins() -> list[str]:
    """List all available output framework plugins."""
    registry = PluginRegistry()
    return registry.list_available_plugins()

def list_available_ai_providers() -> list[str]:
    """List all available AI providers."""
    factory = AIProviderFactory()
    return factory.list_available_providers() 