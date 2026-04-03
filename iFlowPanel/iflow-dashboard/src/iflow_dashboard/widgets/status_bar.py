"""Status bar widget - Show connection status and keyboard hints."""

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Horizontal

from ..config import KEY_BINDINGS


class StatusBar(Widget):
    """
    Status bar showing current status and keyboard shortcuts.

    Displayed at the bottom of the application.
    """

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $background;
        padding: 0 1;
    }
    StatusBar .left {
        text-align: left;
    }
    StatusBar .right {
        text-align: right;
    }
    StatusBar .dim {
        color: $background;
        text-opacity: 0.7;
    }
    """

    # Reactive status messages
    status_message: reactive[str] = reactive("Ready")
    cli_alive: reactive[bool] = reactive(False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._focus = "cli"  # "cli" or "sidebar"

    def render(self) -> str:
        # Status indicator
        status_icon = "●" if self.cli_alive else "○"
        status_text = f"{status_icon} {self.status_message}"

        # Focus indicator
        focus_indicator = f"[F: {self._focus.upper()}]"

        # Key hints
        hints = self._get_key_hints()

        # Layout: status | focus | hints
        left = f"{status_text}  {focus_indicator}"
        right = hints

        return f"{left}  [dim]│[/]  {right}"

    def _get_key_hints(self) -> str:
        """Get keyboard shortcut hints."""
        hints = []
        hints.append(f"[dim]Quit:[/] {KEY_BINDINGS['quit'].upper()}")
        hints.append(f"[dim]Switch:[/] TAB")
        hints.append(f"[dim]Refresh:[/] {KEY_BINDINGS['refresh'].upper()}")
        return "  ".join(hints)

    def set_status(self, message: str) -> None:
        """Update the status message."""
        self.status_message = message

    def set_cli_alive(self, alive: bool) -> None:
        """Update CLI alive status."""
        self.cli_alive = alive

    def set_focus(self, focus: str) -> None:
        """Update which pane has focus."""
        self._focus = focus
        self.refresh()

    def on_focus(self) -> None:
        """Handle focus events."""
        pass  # Status bar doesn't take focus
