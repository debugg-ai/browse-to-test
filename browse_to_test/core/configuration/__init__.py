"""
Configuration and template management components.
"""

from .config import Config, AIConfig, OutputConfig, SharedSetupConfig
from .language_templates import LanguageTemplateManager, LanguageTemplate
from .shared_setup_manager import SharedSetupManager, SetupUtility
from .comment_manager import CommentManager, CommentStyle
from ...output_langs import LanguageManager

__all__ = [
    "Config",
    "AIConfig",
    "OutputConfig", 
    "SharedSetupConfig",
    "LanguageTemplateManager",
    "LanguageTemplate",
    "SharedSetupManager",
    "SetupUtility",
    "CommentManager",
    "CommentStyle",
    "LanguageManager",
] 