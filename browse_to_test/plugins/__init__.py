"""
Plugin system for browse-to-test library.

Supports different output frameworks and languages.
"""

from .registry import PluginRegistry
from .base import OutputPlugin, PluginError

__all__ = [
    "PluginRegistry",
    "OutputPlugin", 
    "PluginError",
] 