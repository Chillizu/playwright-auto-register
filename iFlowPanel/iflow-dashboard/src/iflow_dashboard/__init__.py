"""iFlow Dashboard - TUI wrapper for iFlow CLI with status panel."""

from .app import iFlowDashboardApp, main
from .config import IFLOW_DIR, STATE_FILE, THEME, KEY_BINDINGS
from .core import StateManager, StateMonitor, Subagent, TaskInfo, TaskStatus, AppState

__version__ = "0.1.0"

__all__ = [
    "iFlowDashboardApp",
    "main",
    "IFLOW_DIR",
    "STATE_FILE",
    "THEME",
    "KEY_BINDINGS",
    "StateManager",
    "StateMonitor",
    "Subagent",
    "TaskInfo",
    "TaskStatus",
    "AppState",
]