"""Main application entry point for iFlow Dashboard."""

import asyncio
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.theme import Theme

from .config import KEY_BINDINGS
from .core.state import StateManager
from .core.monitor import StateMonitor
from .widgets.cli_pane import CLIPane, CLIExited
from .widgets.sidebar import Sidebar
from .widgets.status_bar import StatusBar


class MainScreen(Screen):
    """Main screen containing all widgets."""

    CSS = """
    Horizontal {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Sidebar(id="sidebar"),
            CLIPane(id="cli-pane"),
        )
        yield StatusBar(id="status-bar")


class iFlowDashboardApp(App):
    """
    iFlow Dashboard - TUI wrapper for iFlow CLI.

    A dashboard that embeds iFlow CLI with an external status panel
    showing subagent activity and task progress.
    """

    CSS = """
    Screen {
        background: $background;
    }
    """

    # Register custom theme
    THEMES = {
        "iflow": Theme(
            name="iflow",
            primary="#00d4aa",
            secondary="#6c7086",
            accent="#f38ba8",
            background="#1e1e2e",
            surface="#313244",
            panel="#313244",
            boost="#f38ba8",
            dark=True,
            variables={
                "text": "#cdd6f4",
                "success": "#a6e3a1",
                "warning": "#f9e2af",
                "error": "#f38ba8",
            },
        ),
    }

    # Set default theme
    DEFAULT_THEME = "iflow"

    BINDINGS = [
        (KEY_BINDINGS["quit"], "quit", "Quit"),
        (KEY_BINDINGS["help"], "help", "Help"),
        (KEY_BINDINGS["refresh"], "refresh_state", "Refresh"),
        ("tab", "switch_focus", "Switch Focus"),
        ("shift+tab", "switch_focus_reverse", "Switch Focus (Reverse)"),
    ]

    # Reactive state
    focus: reactive[str] = reactive("cli")

    def __init__(self, command: str = "iflow", **kwargs) -> None:
        super().__init__(**kwargs)
        self._command = command
        self._state_monitor: Optional[StateMonitor] = None

    def on_mount(self) -> None:
        """Initialize state monitor and set up focus."""
        # Start state monitor
        self._state_monitor = StateMonitor()
        self._state_monitor.add_callback(self._on_state_change)
        self._state_monitor.start()

        # Set initial focus
        self._update_focus()

        # Update status bar
        self._update_status("Dashboard started")

    def on_unmount(self) -> None:
        """Clean up resources."""
        if self._state_monitor:
            self._state_monitor.stop()
            self._state_monitor = None

    def compose(self) -> ComposeResult:
        yield MainScreen()

    def _on_state_change(self) -> None:
        """Callback when state file changes."""
        # Refresh sidebar
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.refresh_state()

        # Update status bar with current activity
        self._update_status_from_state()

    def _update_status_from_state(self) -> None:
        """Update status bar based on current state."""
        manager = StateManager()
        state = manager.load()

        active_subagents = len([s for s in state.subagents if s.status == "active"])
        running_tasks = len([t for t in state.tasks if t.status.value == "running"])

        if active_subagents > 0 or running_tasks > 0:
            status = f"{active_subagents} agents · {running_tasks} tasks"
        else:
            status = "Ready"

        self._update_status(status)

    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        try:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_status(message)
        except Exception:
            pass

    def _update_focus(self) -> None:
        """Update which pane has focus."""
        try:
            cli_pane = self.query_one("#cli-pane", CLIPane)
            status_bar = self.query_one("#status-bar", StatusBar)

            if self.focus == "cli":
                cli_pane.focus()
                status_bar.set_focus("cli")
            else:
                status_bar.set_focus("sidebar")
        except Exception:
            pass

    def action_switch_focus(self) -> None:
        """Switch focus between CLI and sidebar."""
        self.focus = "sidebar" if self.focus == "cli" else "cli"
        self._update_focus()

    def action_switch_focus_reverse(self) -> None:
        """Switch focus in reverse direction."""
        self.action_switch_focus()

    def action_refresh_state(self) -> None:
        """Manually refresh state from file."""
        self._on_state_change()
        self._update_status("State refreshed")

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())

    # Handle CLI events
    def on_cli_exited(self, event: CLIExited) -> None:
        """Handle CLI process exit."""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_cli_alive(False)
        status_bar.set_status(f"CLI exited (code: {event.exit_code})")

    def on_cli_output(self, event) -> None:
        """Handle CLI output - update alive status."""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_cli_alive(True)


class HelpScreen(Screen):
    """Help screen showing key bindings."""

    CSS = """
    HelpScreen {
        align: center middle;
    }
    HelpScreen Container {
        background: $surface;
        padding: 2;
        border: solid $primary;
        width: 50;
    }
    HelpScreen .title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    HelpScreen .binding {
        margin: 0 0 1 0;
    }
    HelpScreen .key {
        color: $accent;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        from textual.containers import Container, Vertical

        bindings_text = "\n".join([
            f"[key]{k}[/]  [dim]{d}[/]"
            for k, d in [
                ("TAB", "Switch Focus"),
                ("Q", "Quit"),
                ("R", "Refresh"),
                ("?", "Help"),
                ("Ctrl+C", "Interrupt CLI"),
                ("Ctrl+D", "Send EOF"),
                ("Ctrl+L", "Clear Screen"),
            ]
        ])

        yield Container(
            Vertical(
                "[title]iFlow Dashboard Help[/]",
                "",
                bindings_text,
                "",
                "[dim]Press ESC or Q to close[/]",
            )
        )


def main() -> None:
    """Main entry point."""
    import sys

    # Allow passing a different command
    command = sys.argv[1] if len(sys.argv) > 1 else "iflow"

    app = iFlowDashboardApp(command=command)
    app.run()


if __name__ == "__main__":
    main()
