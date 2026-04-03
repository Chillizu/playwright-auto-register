"""Core modules for iFlow Dashboard."""

from .state import StateManager, Subagent, TaskInfo, TaskStatus, AppState
from .monitor import StateMonitor

__all__ = [
    "StateManager",
    "Subagent", 
    "TaskInfo",
    "TaskStatus",
    "AppState",
    "StateMonitor",
]