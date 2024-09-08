import atexit
import os
import signal
import tempfile
import psutil
import time
from typing import Callable, Optional

from snap_sweep.snap_sweep_app import SnapSweepApp


class AppManager:
    def __init__(self):
        self.app: Optional[SnapSweepApp] = None
        self.lock_file: str = os.path.join(tempfile.gettempdir(), "snap_sweep.lock")

    def is_already_running(self) -> bool:
        if os.path.exists(self.lock_file):
            with open(self.lock_file, "r") as f:
                pid, timestamp = map(int, f.read().split())

            # Check if the process is still running
            if psutil.pid_exists(pid):
                return True

            # If the process is not running but the file is older than 1 hour, assume it's stale
            if time.time() - timestamp > 3600:
                os.remove(self.lock_file)
            else:
                return True

        with open(self.lock_file, "w") as f:
            f.write(f"{os.getpid()} {int(time.time())}")

        return False

    def setup_signals(self, root, app: SnapSweepApp, on_closing: Callable[[], None]):
        self.app = app
        root.protocol("WM_DELETE_WINDOW", on_closing)
        atexit.register(self.cleanup_lock_file)
        signal.signal(signal.SIGINT, lambda sig, frame: on_closing())
        signal.signal(signal.SIGTERM, lambda sig, frame: on_closing())

    def cleanup_lock_file(self):
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
