"""Backward compatibility module for session components."""

# Re-export SessionResult from executor for backward compatibility
from ..executor import SessionResult, IncrementalSession

__all__ = [
    "SessionResult",
    "IncrementalSession"
]