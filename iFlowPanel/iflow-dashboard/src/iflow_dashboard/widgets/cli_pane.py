"""CLI pane widget - PTY-based terminal embedding for iFlow CLI."""

import asyncio
import os
import pty
import signal
import struct
import fcntl
import termios
from typing import Optional

from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive


class CLIOutput(Message):
    """Message sent when CLI produces output."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        super().__init__()


class CLIExited(Message):
    """Message sent when CLI process exits."""

    def __init__(self, exit_code: int) -> None:
        self.exit_code = exit_code
        super().__init__()


class CLIPane(Widget):
    """
    A widget that embeds an interactive terminal running iFlow CLI.

    Uses PTY (pseudo-terminal) for proper terminal emulation.
    """

    DEFAULT_CSS = """
    CLIPane {
        background: $background;
        color: $text;
        height: 1fr;
        overflow: hidden;
    }
    """

    BINDINGS = [
        ("ctrl+c", "send_interrupt", "Send Ctrl+C"),
        ("ctrl+d", "send_eof", "Send Ctrl+D"),
        ("ctrl+l", "clear_screen", "Clear Screen"),
    ]

    # The command to run (default: iflow)
    command: reactive[str] = reactive("iflow")

    def __init__(
        self,
        command: str = "iflow",
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.command = command

        # PTY file descriptors
        self._master_fd: int = -1
        self._slave_fd: int = -1

        # Process ID
        self._pid: int = -1

        # Read task
        self._read_task: Optional[asyncio.Task] = None

        # Output buffer for rendering
        self._buffer: bytearray = bytearray()

    def on_mount(self) -> None:
        """Start the CLI process when widget is mounted."""
        self._start_cli()

    def on_unmount(self) -> None:
        """Clean up CLI process when widget is unmounted."""
        self._stop_cli()

    def _start_cli(self) -> None:
        """Start the CLI process in a PTY."""
        # Create pseudo-terminal pair
        self._master_fd, self._slave_fd = pty.openpty()

        # Set terminal size
        self._set_pty_size()

        # Fork process
        self._pid = os.fork()

        if self._pid == 0:
            # Child process
            os.setsid()

            # Set controlling terminal
            fcntl.ioctl(self._slave_fd, termios.TIOCSCTTY, 0)

            # Redirect stdio to slave PTY
            os.dup2(self._slave_fd, 0)  # stdin
            os.dup2(self._slave_fd, 1)  # stdout
            os.dup2(self._slave_fd, 2)  # stderr

            # Close master fd in child
            os.close(self._master_fd)

            # Set environment
            os.environ["TERM"] = "xterm-256color"
            os.environ["COLORTERM"] = "truecolor"

            # Execute command
            try:
                os.execvp(self.command, [self.command])
            except Exception as e:
                os._exit(1)
        else:
            # Parent process
            os.close(self._slave_fd)
            self._slave_fd = -1

            # Set non-blocking mode on master
            flags = fcntl.fcntl(self._master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self._master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Start reading output
            self._read_task = asyncio.create_task(self._read_output())

    def _stop_cli(self) -> None:
        """Stop the CLI process."""
        # Cancel read task
        if self._read_task:
            self._read_task.cancel()
            self._read_task = None

        # Kill process if running
        if self._pid > 0:
            try:
                os.kill(self._pid, signal.SIGTERM)
                os.waitpid(self._pid, os.WNOHANG)
            except ProcessLookupError:
                pass
            self._pid = -1

        # Close file descriptors
        if self._master_fd >= 0:
            os.close(self._master_fd)
            self._master_fd = -1

    def _set_pty_size(self) -> None:
        """Set the PTY size based on widget dimensions."""
        if self._master_fd < 0:
            return

        # Get widget size (fallback to reasonable defaults)
        width = max(self.size.width, 80)
        height = max(self.size.height, 24)

        # Set terminal size using ioctl
        winsize = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)

    def on_resize(self) -> None:
        """Handle terminal resize."""
        self._set_pty_size()

    async def _read_output(self) -> None:
        """Read output from the PTY in a background task."""
        loop = asyncio.get_event_loop()

        while True:
            try:
                # Read from master FD
                data = await loop.run_in_executor(None, self._read_chunk)

                if data:
                    self._buffer.extend(data)
                    self.post_message(CLIOutput(data))
                    self.refresh()

            except asyncio.CancelledError:
                break
            except Exception:
                # Check if process has exited
                if self._pid > 0:
                    try:
                        pid, status = os.waitpid(self._pid, os.WNOHANG)
                        if pid == self._pid:
                            exit_code = os.WEXITSTATUS(status)
                            self.post_message(CLIExited(exit_code))
                            break
                    except ChildProcessError:
                        break

    def _read_chunk(self, size: int = 4096) -> bytes:
        """Read a chunk of data from the PTY."""
        try:
            return os.read(self._master_fd, size)
        except BlockingIOError:
            return b""
        except OSError:
            return b""

    def write(self, data: bytes | str) -> None:
        """Write data to the CLI's stdin."""
        if self._master_fd < 0:
            return

        if isinstance(data, str):
            data = data.encode("utf-8")

        try:
            os.write(self._master_fd, data)
        except OSError:
            pass

    def action_send_interrupt(self) -> None:
        """Send interrupt signal (Ctrl+C)."""
        self.write(b"\x03")

    def action_send_eof(self) -> None:
        """Send EOF (Ctrl+D)."""
        self.write(b"\x04")

    def action_clear_screen(self) -> None:
        """Clear the screen."""
        self.write(b"\x0c")

    def on_key(self, event) -> None:
        """Handle keyboard input."""
        # Don't capture binding keys
        if event.key in ("ctrl+c", "ctrl+d", "ctrl+l"):
            return

        # Send key to terminal
        if event.character:
            self.write(event.character)
        elif event.key == "enter":
            self.write("\r")
        elif event.key == "tab":
            self.write("\t")
        elif event.key == "backspace":
            self.write("\x7f")
        elif event.key == "up":
            self.write("\x1b[A")
        elif event.key == "down":
            self.write("\x1b[B")
        elif event.key == "right":
            self.write("\x1b[C")
        elif event.key == "left":
            self.write("\x1b[D")
        elif event.key == "escape":
            self.write("\x1b")

        event.stop()

    def render(self) -> str:
        """Render the terminal output."""
        try:
            # Decode buffer as UTF-8, replacing errors
            text = self._buffer.decode("utf-8", errors="replace")

            # Limit buffer size to prevent memory issues
            max_size = 100000
            if len(self._buffer) > max_size:
                self._buffer = self._buffer[-max_size:]
                text = "...[truncated]...\n" + text[-max_size:]

            return text
        except Exception:
            return ""

    def is_alive(self) -> bool:
        """Check if the CLI process is still running."""
        if self._pid <= 0:
            return False

        try:
            pid, _ = os.waitpid(self._pid, os.WNOHANG)
            return pid == 0
        except ChildProcessError:
            return False