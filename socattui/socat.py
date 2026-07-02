"""Socat process manager for starting/stopping bridges."""

import os
import signal
import subprocess
import sys
from pathlib import Path

from .config import Config, Bridge, load_config, save_config


PID_DIR = Path.home() / ".config" / "socattui" / "pids"


def _ensure_pid_dir() -> None:
    """Create PID directory if it doesn't exist."""
    PID_DIR.mkdir(parents=True, exist_ok=True)


def _pid_file(bridge: Bridge) -> Path:
    """Get PID file path for a bridge."""
    safe_name = bridge.name.replace(" ", "_").replace("/", "_")
    return PID_DIR / f"{safe_name}.pid"


def is_running(bridge: Bridge) -> bool:
    """Check if a bridge's socat process is running."""
    pid_file = _pid_file(bridge)
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 0)  # Check if process exists
        return True
    except (ProcessLookupError, ValueError, PermissionError):
        pid_file.unlink(missing_ok=True)
        return False


def get_pid(bridge: Bridge) -> int | None:
    """Get PID of running bridge, or None."""
    pid_file = _pid_file(bridge)
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text().strip())
    except ValueError:
        return None


def start_bridge(bridge: Bridge, detached: bool = True) -> bool:
    """Start a socat bridge. Returns True if started successfully."""
    _ensure_pid_dir()

    if is_running(bridge):
        return True  # Already running

    cmd = _build_socat_cmd(bridge)

    try:
        if detached:
            # Start detached process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            # Save PID
            _pid_file(bridge).write_text(str(process.pid))
        else:
            # Start in foreground (for debugging)
            subprocess.run(cmd, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Failed to start {bridge.name}: {e}", file=sys.stderr)
        return False


def stop_bridge(bridge: Bridge) -> bool:
    """Stop a socat bridge. Returns True if stopped successfully."""
    pid_file = _pid_file(bridge)
    if not pid_file.exists():
        return True  # Already stopped

    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        # Wait briefly for process to stop
        import time
        time.sleep(0.1)
        try:
            os.kill(pid, 0)
            # Still running, force kill
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except (ProcessLookupError, ValueError, PermissionError):
        pass
    finally:
        pid_file.unlink(missing_ok=True)

    return True


def start_all(config: Config | None = None, detached: bool = True) -> dict[str, bool]:
    """Start all configured bridges. Returns dict of name -> success."""
    if config is None:
        config = load_config()

    results = {}
    for bridge in config.bridges:
        results[bridge.name] = start_bridge(bridge, detached)
    return results


def stop_all(config: Config | None = None) -> dict[str, bool]:
    """Stop all configured bridges. Returns dict of name -> success."""
    if config is None:
        config = load_config()

    results = {}
    for bridge in config.bridges:
        results[bridge.name] = stop_bridge(bridge)
    return results


def get_status(config: Config | None = None) -> dict[str, dict]:
    """Get status of all bridges. Returns dict of name -> {running, pid}."""
    if config is None:
        config = load_config()

    status = {}
    for bridge in config.bridges:
        running = is_running(bridge)
        pid = get_pid(bridge) if running else None
        status[bridge.name] = {"running": running, "pid": pid}
    return status


def _build_socat_cmd(bridge: Bridge) -> list[str]:
    """Build socat command for a bridge."""
    tcp_part = f"TCP-LISTEN:{bridge.port},fork,reuseaddr"
    file_part = f"FILE:{bridge.device},b{bridge.baudrate},raw,echo=0"
    return ["socat", tcp_part, file_part]
