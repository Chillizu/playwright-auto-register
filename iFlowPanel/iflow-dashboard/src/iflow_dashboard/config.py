"""Configuration for iFlow Dashboard."""

from pathlib import Path

# State file location
IFLOW_DIR = Path.home() / ".iflow"
STATE_FILE = IFLOW_DIR / "state.json"

# TUI settings
SIDEBAR_WIDTH = 32
STATUS_BAR_HEIGHT = 1

# Colors (textual CSS will use these)
THEME = {
    "primary": "#00d4aa",
    "secondary": "#6c7086",
    "accent": "#f38ba8",
    "background": "#1e1e2e",
    "surface": "#313244",
    "text": "#cdd6f4",
    "success": "#a6e3a1",
    "warning": "#f9e2af",
    "error": "#f38ba8",
}

# Key bindings
KEY_BINDINGS = {
    "quit": "q",
    "help": "?",
    "refresh": "s",
    "tasks": "t",
    "switch_focus": "tab",
}
