"""File-based state monitoring using watchdog."""

import asyncio
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from ..config import STATE_FILE


class StateFileHandler(FileSystemEventHandler):
    """Handler for state file changes."""

    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self._last_modified = 0.0

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory:
            return

        # Check if it's the state file
        path = Path(event.src_path)
        if path.name == STATE_FILE.name:
            # Debounce: ignore rapid consecutive events
            import time
            now = time.time()
            if now - self._last_modified > 0.1:
                self._last_modified = now
                self.callback()


class StateMonitor:
    """Monitors state file changes and notifies listeners."""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self._observer: Observer | None = None
        self._callbacks: list[Callable[[], None]] = []

    def add_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback to be called on state changes."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify(self) -> None:
        """Notify all callbacks."""
        for callback in self._callbacks:
            try:
                callback()
            except Exception:
                pass  # Don't let one callback failure stop others

    def start(self) -> None:
        """Start monitoring the state file."""
        if self._observer is not None:
            return

        self._observer = Observer()
        handler = StateFileHandler(self._notify)

        # Watch the parent directory (more reliable than watching file directly)
        watch_path = self.state_file.parent
        if watch_path.exists():
            self._observer.schedule(handler, str(watch_path), recursive=False)
            self._observer.start()

    def stop(self) -> None:
        """Stop monitoring."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def __enter__(self) -> "StateMonitor":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()


# Global monitor instance
_state_monitor: StateMonitor | None = None


def get_state_monitor() -> StateMonitor:
    """Get the global state monitor instance."""
    global _state_monitor
    if _state_monitor is None:
        _state_monitor = StateMonitor()
    return _state_monitor
