import os
import sys
import tempfile
import atexit
import signal
from tkinter import PhotoImage

import customtkinter as ctk

from snap_sweep.snap_sweep_app import SnapSweepApp


def create_app():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme(
        os.path.join(os.path.dirname(__file__), "resources", "sky.json")
    )

    root = ctk.CTk()
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
    img = PhotoImage(file=icon_path)
    root.wm_iconphoto(True, img)

    root.title("Smart Snap Sweep")
    root.geometry("1600x1024")
    # Configure the grid system
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)

    app = SnapSweepApp(root)

    return root, app


def is_already_running():
    temp_dir = tempfile.gettempdir()
    lock_file = os.path.join(temp_dir, "snap_sweep.lock")

    if os.path.exists(lock_file):
        return True

    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))

    return False


def cleanup_lock_file():
    try:
        os.remove(os.path.join(tempfile.gettempdir(), "snap_sweep.lock"))
    except FileNotFoundError:
        pass


def main():
    if is_already_running():
        print("SnapSweep is already running.")
        sys.exit(1)

    root, app = create_app()
    app.setup_ui()

    def on_closing():
        app.cleanup()
        root.destroy()
        cleanup_lock_file()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    atexit.register(cleanup_lock_file)
    signal.signal(signal.SIGINT, lambda sig, frame: on_closing())
    signal.signal(signal.SIGTERM, lambda sig, frame: on_closing())

    root.mainloop()


if __name__ == "__main__":
    app_env = os.getenv("APP_ENV", "development")
    print("Running in", app_env, "mode")
    if app_env != "production":
        from hupper import start_reloader

        reloader = start_reloader("snap_sweep.__main__.main")
    else:
        main()
