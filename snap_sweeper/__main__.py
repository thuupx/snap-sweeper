import os
import sys
from tkinter import PhotoImage

import customtkinter as ctk

from snap_sweeper.app_manager import AppManager
from snap_sweeper.snap_sweeper_app import SnapSweeperApp


class SnapSweeperLauncher:
    def __init__(self):
        self.app_manager = AppManager()

    def create_app(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme(
            os.path.join(os.path.dirname(__file__), "resources", "sky.json")
        )

        self.root = ctk.CTk()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        img = PhotoImage(file=icon_path)
        self.root.wm_iconphoto(True, img)

        self.root.title("Smart Snap Sweep")
        self.root.geometry("1600x1024")
        # Configure the grid system
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        self.app = SnapSweeperApp(self.root)

    def setup_app(self):
        self.app.setup_ui()
        self.app.setup_event_loop()

    def run(self):
        if self.app_manager.is_already_running():
            print("SnapSweep is already running.")
            self.app_manager.cleanup_lock_file()
            sys.exit(1)

        self.create_app()
        self.setup_app()
        self.app_manager.setup_signals(self.root, self.app, self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.app.cleanup()
        self.root.destroy()
        self.app_manager.cleanup_lock_file()
        sys.exit(0)


def main():
    launcher = SnapSweeperLauncher()
    launcher.run()


if __name__ == "__main__":
    app_env = os.getenv("APP_ENV", "development")
    print("Running in", app_env, "mode")
    if app_env != "production":
        from hupper import start_reloader

        reloader = start_reloader("snap_sweeper.__main__.main")
    else:
        main()
