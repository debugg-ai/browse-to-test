"""Backward compatibility module for orchestration components."""

# Re-export components that were moved to executor
from ..executor import SessionResult, IncrementalSession, BTTExecutor

# Import session submodule to make it available
from . import session

__all__ = [
    "SessionResult",
    "IncrementalSession", 
    "BTTExecutor",
    "session"
]