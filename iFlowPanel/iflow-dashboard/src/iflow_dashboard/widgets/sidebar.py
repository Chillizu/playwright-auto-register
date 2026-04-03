"""Sidebar widget - Display subagents and tasks from state."""

from typing import Optional

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Vertical, VerticalScroll
from textual.app import ComposeResult
from textual.widgets import Static

from ..core.state import StateManager, Subagent, TaskInfo, TaskStatus


class SubagentItem(Widget):
    """A single subagent display item."""

    DEFAULT_CSS = """
    SubagentItem {
        padding: 0 1;
        margin: 0 0 1 0;
        height: auto;
    }
    SubagentItem:hover {
        background: $surface;
    }
    SubagentItem .name {
        color: $primary;
        text-style: bold;
    }
    SubagentItem .model {
        color: $secondary;
    }
    SubagentItem .status-active {
        color: $success;
    }
    SubagentItem .status-idle {
        color: $warning;
    }
    """

    def __init__(self, subagent, **kwargs) -> None:
        super().__init__(**kwargs)
        self._subagent = subagent

    def render(self) -> str:
        status_icon = "●" if self._subagent.status == "active" else "○"
        status_class = "status-active" if self._subagent.status == "active" else "status-idle"
        return f"[{status_class}]{status_icon}[/] [{status_class}]{self._subagent.status}[/]\n  [bold]{self._subagent.name}[/]\n  [dim]{self._subagent.model}[/]"


class TaskItem(Widget):
    """A single task display item."""

    DEFAULT_CSS = """
    TaskItem {
        padding: 0 1;
        margin: 0 0 1 0;
        height: auto;
    }
    TaskItem:hover {
        background: $surface;
    }
    TaskItem .progress {
        color: $accent;
    }
    """

    STATUS_ICONS = {
        TaskStatus.PENDING: "○",
        TaskStatus.RUNNING: "◐",
        TaskStatus.COMPLETED: "●",
        TaskStatus.FAILED: "✗",
        "pending": "○",
        "running": "◐",
        "completed": "●",
        "failed": "✗",
    }

    STATUS_COLORS = {
        TaskStatus.PENDING: "dim",
        TaskStatus.RUNNING: "warning",
        TaskStatus.COMPLETED: "success",
        TaskStatus.FAILED: "error",
        "pending": "dim",
        "running": "warning",
        "completed": "success",
        "failed": "error",
    }

    def __init__(self, task, **kwargs) -> None:
        super().__init__(**kwargs)
        self._task = task

    def render(self) -> str:
        icon = self.STATUS_ICONS.get(self._task.status, "○")
        color = self.STATUS_COLORS.get(self._task.status, "dim")
        
        # Get status string
        status_str = self._task.status.value if hasattr(self._task.status, 'value') else str(self._task.status)

        lines = [f"[{color}]{icon}[/] [{color}]{status_str}[/] [bold]{self._task.name}[/]"]

        if self._task.progress is not None and self._task.progress > 0:
            bar = self._render_progress_bar(self._task.progress)
            lines.append(f"  {bar}")

        if self._task.subagent_id:
            lines.append(f"  [dim]by {self._task.subagent_id[:8]}...[/]")

        return "\n".join(lines)

    def _render_progress_bar(self, progress: float, width: int = 20) -> str:
        """Render a simple progress bar."""
        filled = int(progress * width)
        empty = width - filled
        return f"[primary]{'━' * filled}[/][dim]{'─' * empty}[/] {progress:.0%}"


class Sidebar(Widget):
    """
    Sidebar displaying current subagents and tasks.

    Reads from the shared StateManager and updates reactively.
    """

    DEFAULT_CSS = """
    Sidebar {
        width: 32;
        dock: left;
        background: $surface;
        border-right: solid $primary;
    }
    Sidebar .header {
        color: $primary;
        text-style: bold;
        padding: 1;
        border-bottom: solid $secondary;
    }
    Sidebar VerticalScroll {
        height: 1fr;
    }
    """

    # Reactive state (no type annotations to avoid Task name collision with asyncio.Task)
    subagents = reactive([])
    tasks = reactive([])

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._state_manager = StateManager()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Vertical(
                Static("[bold]Subagents[/]", classes="header-text"),
                classes="header",
                id="subagents-header",
            ),
            VerticalScroll(id="subagents-list"),
            Vertical(
                Static("[bold]Tasks[/]", classes="header-text"),
                classes="header",
                id="tasks-header",
            ),
            VerticalScroll(id="tasks-list"),
        )

    def on_mount(self) -> None:
        """Initial load of state."""
        # Delay state loading to ensure widgets are fully mounted
        self.set_timer(0.1, self._load_state)

    def _load_state(self) -> None:
        """Load state from StateManager."""
        state = self._state_manager.load()
        self.subagents = state.subagents
        self.tasks = state.tasks
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with current data."""
        # Update subagents list
        subagents_list = self.query_one("#subagents-list")
        subagents_list.remove_children()
        for subagent in self.subagents:
            subagents_list.mount(SubagentItem(subagent))

        if not self.subagents:
            subagents_list.mount(Static("[dim]No active subagents[/]"))

        # Update tasks list
        tasks_list = self.query_one("#tasks-list")
        tasks_list.remove_children()
        for task in self.tasks:
            tasks_list.mount(TaskItem(task))

        if not self.tasks:
            tasks_list.mount(Static("[dim]No tasks[/]"))

    def refresh_state(self) -> None:
        """Refresh state from file - call this when state changes."""
        self._load_state()

    def get_active_subagents(self):
        """Get list of currently active subagents."""
        return [s for s in self.subagents if s.status == "active"]

    def get_running_tasks(self):
        """Get list of currently running tasks."""
        return [t for t in self.tasks if t.status == "running" or t.status == TaskStatus.RUNNING.value]