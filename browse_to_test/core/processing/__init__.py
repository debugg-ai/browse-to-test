"""
Input and data processing components for browser automation data.
"""

from .input_parser import InputParser, ParsedAutomationData, ParsedAction
from .action_analyzer import ActionAnalyzer, ActionAnalysisResult, ComprehensiveAnalysisResult
from .context_collector import ContextCollector, SystemContext

__all__ = [
    "InputParser",
    "ParsedAutomationData", 
    "ParsedAction",
    "ActionAnalyzer",
    "ActionAnalysisResult",
    "ComprehensiveAnalysisResult",
    "ContextCollector",
    "SystemContext",
] 