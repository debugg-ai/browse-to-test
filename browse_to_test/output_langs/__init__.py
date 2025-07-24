"""
Output Language Generation System for browse-to-test.

This module provides a modular, framework-agnostic system for generating 
test scripts in multiple programming languages. It replaces the old 
language_utils with proper naming conventions and better separation of concerns.

Key Features:
- Modular language support with dedicated generators per language/framework
- Template-based code generation with external template files
- Shared constants and patterns across languages
- Clean integration with existing codebase
- Extensible architecture for adding new languages

Usage:
    from browse_to_test.output_langs import LanguageManager
    
    # Initialize for Python + Playwright
    manager = LanguageManager(language='python', framework='playwright')
    
    # Generate utilities and constants
    utils_code = manager.generate_utilities()
    constants_code = manager.generate_constants()
    
    # Generate complete test script
    test_script = manager.generate_test_script(automation_data)
"""

from typing import List
from .manager import LanguageManager
from .registry import LanguageRegistry, SupportedLanguage, SupportedFramework
from .exceptions import (
    LanguageNotSupportedError,
    FrameworkNotSupportedError, 
    TemplateGenerationError,
    CodeGenerationError
)

# Version info
__version__ = "1.0.0"
__author__ = "browse-to-test team"

# Main exports
__all__ = [
    'LanguageManager',
    'LanguageRegistry', 
    'SupportedLanguage',
    'SupportedFramework',
    'LanguageNotSupportedError',
    'FrameworkNotSupportedError',
    'TemplateGenerationError', 
    'CodeGenerationError',
    'get_supported_languages',
    'get_supported_frameworks',
    'create_language_manager'
]

# Convenience functions

def get_supported_languages() -> List[str]:
    """Get list of all supported programming languages."""
    registry = LanguageRegistry()
    return registry.get_supported_languages()

def get_supported_frameworks() -> List[str]:
    """Get list of all supported testing frameworks."""
    registry = LanguageRegistry()
    return registry.get_supported_frameworks()

def create_language_manager(language: str, framework: str, **kwargs) -> LanguageManager:
    """
    Create a language manager for the specified language and framework.
    
    Args:
        language: Target programming language (python, typescript, javascript, csharp, java)
        framework: Target testing framework (playwright, selenium, etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Configured LanguageManager instance
        
    Raises:
        LanguageNotSupportedError: If language is not supported
        FrameworkNotSupportedError: If framework is not supported for the language
    """
    return LanguageManager(language=language, framework=framework, **kwargs) 