"""
Browse-to-Test: AI-Powered Browser Automation to Test Script Converter

A Python library that uses AI to convert browser automation data into test scripts
for various testing frameworks (Playwright, Selenium, etc.).

Now includes incremental live update functionality for real-time test generation.
"""

from .core.orchestrator import TestScriptOrchestrator
from .core.incremental_orchestrator import IncrementalTestScriptOrchestrator, ScriptState, IncrementalUpdateResult
from .core.config import Config, AIConfig, OutputConfig, ProcessingConfig
from .plugins.registry import PluginRegistry
from .ai.factory import AIProviderFactory

__version__ = "0.2.0"
__author__ = "Browse-to-Test Contributors"

# Main API exports
__all__ = [
    # Original batch processing
    "TestScriptOrchestrator",
    "Config", 
    "AIConfig",
    "OutputConfig",
    "ProcessingConfig",
    "PluginRegistry",
    "AIProviderFactory",
    "convert_to_test_script",
    "list_available_plugins",
    "list_available_ai_providers",
    
    # New incremental processing
    "IncrementalTestScriptOrchestrator",
    "ScriptState",
    "IncrementalUpdateResult",
    "start_incremental_session",
    "add_incremental_step",
    "finalize_incremental_session",
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


def start_incremental_session(
    output_framework: str = "playwright",
    target_url: str = None,
    config: dict = None,
    context_hints: dict = None
) -> tuple[IncrementalTestScriptOrchestrator, IncrementalUpdateResult]:
    """
    Start an incremental test script generation session.
    
    This begins the live update workflow where test steps can be added incrementally.
    
    Args:
        output_framework: Target test framework ('playwright', 'selenium', etc.)
        target_url: URL being tested
        config: Optional configuration dictionary
        context_hints: Optional context hints for the test
        
    Returns:
        Tuple of (orchestrator, setup_result)
        
    Example:
        >>> orchestrator, setup = start_incremental_session("playwright", "https://example.com")
        >>> if setup.success:
        ...     step_result = orchestrator.add_step(step_data)
        ...     final_result = orchestrator.finalize_session()
    """
    from .core.config import Config
    
    # Create configuration
    config_obj = Config.from_dict(config or {})
    config_obj.output.framework = output_framework
    
    # Create incremental orchestrator
    orchestrator = IncrementalTestScriptOrchestrator(config_obj)
    
    # Start session
    setup_result = orchestrator.start_incremental_session(
        target_url=target_url,
        context_hints=context_hints
    )
    
    return orchestrator, setup_result


def add_incremental_step(
    orchestrator: IncrementalTestScriptOrchestrator,
    step_data: dict,
    analyze_step: bool = True
) -> IncrementalUpdateResult:
    """
    Add a step to an active incremental session.
    
    Args:
        orchestrator: Active incremental orchestrator
        step_data: Step data dictionary
        analyze_step: Whether to perform AI analysis
        
    Returns:
        Result of adding the step
        
    Example:
        >>> result = add_incremental_step(orchestrator, step_data)
        >>> if result.success:
        ...     print(f"Added {result.new_lines_added} lines")
    """
    return orchestrator.add_step(step_data, analyze_step=analyze_step)


def finalize_incremental_session(
    orchestrator: IncrementalTestScriptOrchestrator,
    final_validation: bool = True,
    optimize_script: bool = True
) -> IncrementalUpdateResult:
    """
    Finalize an incremental test script generation session.
    
    Args:
        orchestrator: Active incremental orchestrator
        final_validation: Whether to perform final validation
        optimize_script: Whether to apply optimizations
        
    Returns:
        Final result with complete test script
        
    Example:
        >>> final = finalize_incremental_session(orchestrator)
        >>> if final.success:
        ...     with open("test.py", "w") as f:
        ...         f.write(final.updated_script)
    """
    return orchestrator.finalize_session(
        final_validation=final_validation,
        optimize_script=optimize_script
    )


def list_available_plugins() -> list[str]:
    """
    List all available output plugins.
    
    Returns:
        List of plugin names
    """
    registry = PluginRegistry()
    return registry.list_available_plugins()


def list_available_ai_providers() -> list[str]:
    """
    List all available AI providers.
    
    Returns:
        List of provider names
    """
    factory = AIProviderFactory()
    return factory.list_available_providers() 