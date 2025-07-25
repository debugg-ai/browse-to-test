"""
JavaScript language support for browse-to-test output generation.

This module provides JavaScript-specific code generation capabilities for
test automation scripts using various testing frameworks.
"""

from .generators.playwright_generator import PlaywrightJavascriptGenerator

__all__ = [
    'PlaywrightJavascriptGenerator'
] 