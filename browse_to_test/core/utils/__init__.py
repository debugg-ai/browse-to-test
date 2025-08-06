"""Core utility modules for browse-to-test library."""

from .comment_manager import CommentManager, CommentStyle  
from .language_templates import LanguageTemplateManager, LanguageTemplate

__all__ = [
    "CommentManager", 
    "CommentStyle",
    "LanguageTemplateManager",
    "LanguageTemplate",
]