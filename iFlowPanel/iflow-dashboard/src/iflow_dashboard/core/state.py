"""State management with atomic writes."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field, asdict
import tempfile
import os

from ..config import IFLOW_DIR, STATE_FILE
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class Subagent:
    """Represents a running subagent."""
    id: str
    type: str
    status: str  # running, completed, failed, pending
    name: str = ""  # Display name
    model: str = ""  # Model being used
    progress: int = 0  # 0-100
    started_at: str = ""
    message: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()
        if not self.name:
            self.name = f"Agent {self.id}"


@dataclass
class TaskInfo:
    """Represents a task."""
    id: str
    name: str
    status: str  # pending, in_progress, completed, failed
    progress: float = 0.0  # 0.0-1.0
    subagent_id: str = ""  # ID of assigned subagent
    created_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class AppState:
    """Complete application state."""
    session_id: str = ""
    subagents: list = field(default_factory=list)
    tasks: list = field(default_factory=list)
    updated_at: str = ""
    current_mode: str = "idle"  # idle, working, reviewing

    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())[:8]
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "subagents": [asdict(s) if isinstance(s, Subagent) else s for s in self.subagents],
            "tasks": [asdict(t) if isinstance(t, TaskInfo) else t for t in self.tasks],
            "updated_at": self.updated_at,
            "current_mode": self.current_mode,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppState":
        subagents = [
            Subagent(**s) if isinstance(s, dict) else s
            for s in data.get("subagents", [])
        ]
        tasks = [
            TaskInfo(**t) if isinstance(t, dict) else t
            for t in data.get("tasks", [])
        ]
        return cls(
            session_id=data.get("session_id", ""),
            subagents=subagents,
            tasks=tasks,
            updated_at=data.get("updated_at", ""),
            current_mode=data.get("current_mode", "idle"),
        )


class StateManager:
    """Manages state with atomic writes."""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self._state: AppState | None = None
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure state directory exists."""
        IFLOW_DIR.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppState:
        """Load state from file."""
        if self._state is not None:
            return self._state

        if self.state_file.exists():
            try:
                content = self.state_file.read_text()
                if content.strip():
                    data = json.loads(content)
                    self._state = AppState.from_dict(data)
                else:
                    self._state = AppState()
            except (json.JSONDecodeError, KeyError):
                self._state = AppState()
        else:
            self._state = AppState()

        return self._state

    def save(self, state: AppState | None = None) -> None:
        """Save state atomically."""
        if state is not None:
            self._state = state

        if self._state is None:
            return

        self._state.updated_at = datetime.now(timezone.utc).isoformat()

        # Atomic write: write to temp file, then rename
        data = json.dumps(self._state.to_dict(), indent=2, ensure_ascii=False)

        # Use temp file in same directory for atomic rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.state_file.parent,
            prefix=".state_tmp_",
            suffix=".json"
        )

        try:
            with os.fdopen(temp_fd, 'w') as f:
                f.write(data)
            # Atomic rename
            os.replace(temp_path, self.state_file)
        except Exception:
            # Cleanup temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def add_subagent(self, subagent_type: str, message: str = ""):
        """Add a new subagent."""
        state = self.load()
        subagent = Subagent(
            id=f"agent-{len(state.subagents) + 1}",
            type=subagent_type,
            status="running",
            message=message,
        )
        state.subagents.append(subagent)
        self.save(state)
        return subagent

    def update_subagent(self, agent_id: str, **kwargs) -> bool:
        """Update a subagent by ID."""
        state = self.load()
        for i, agent in enumerate(state.subagents):
            if agent.id == agent_id:
                for key, value in kwargs.items():
                    if hasattr(agent, key):
                        setattr(agent, key, value)
                self.save(state)
                return True
        return False

    def remove_subagent(self, agent_id: str) -> bool:
        """Remove a subagent by ID."""
        state = self.load()
        original_len = len(state.subagents)
        state.subagents = [a for a in state.subagents if a.id != agent_id]
        if len(state.subagents) < original_len:
            self.save(state)
            return True
        return False

    def add_task(self, name: str):
        """Add a new task."""
        state = self.load()
        task = TaskInfo(
            id=f"task-{len(state.tasks) + 1}",
            name=name,
            status="pending",
        )
        state.tasks.append(task)
        self.save(state)
        return task

    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task by ID."""
        state = self.load()
        for task in state.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                self.save(state)
                return True
        return False

    def set_mode(self, mode: str) -> None:
        """Set current mode."""
        state = self.load()
        state.current_mode = mode
        self.save(state)

    @property
    def state(self) -> AppState:
        """Get current state, loading if necessary."""
        return self.load()


# Global state manager instance
_state_manager: StateManager | None = None


def get_state_manager() -> StateManager:
    """Get the global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
