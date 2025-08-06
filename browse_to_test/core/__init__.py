"""Core components for the browse-to-test library."""

# Unified configuration system
from .config import Config, ConfigBuilder, ConfigPreset, CommentManager, CommentStyle, LanguageTemplateManager, LanguageTemplate

# Unified execution system
from .executor import BTTExecutor, IncrementalSession, ExecutionResult, SessionResult

# Input/Data processing
from .processing import InputParser, ActionAnalyzer

# Backward compatibility - orchestration module
from . import orchestration

# Backward compatibility
AIConfig = Config
OutputConfig = Config
ProcessingConfig = Config
E2eTestConverter = BTTExecutor
AsyncIncrementalSession = IncrementalSession

__all__ = [
    # New unified API
    "Config",
    "ConfigBuilder", 
    "ConfigPreset",
    "BTTExecutor",
    "IncrementalSession",
    "ExecutionResult",
    "SessionResult",
    
    # Processing components
    "InputParser",
    "ActionAnalyzer",
    
    # Utility components
    "CommentManager",
    "CommentStyle", 
    "LanguageTemplateManager",
    "LanguageTemplate",
    
    # Backward compatibility
    "AIConfig",
    "OutputConfig", 
    "ProcessingConfig",
    "E2eTestConverter",
    "AsyncIncrementalSession",
] 