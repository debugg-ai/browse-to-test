"""
TypeScript language support for browse-to-test output generation.

This module provides TypeScript-specific code generation capabilities for
test automation scripts using various testing frameworks.
"""

from .generators.playwright_generator import PlaywrightTypescriptGenerator

__all__ = [
    'PlaywrightTypescriptGenerator'
] 