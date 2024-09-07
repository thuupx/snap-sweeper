import os
from tkinter import PhotoImage

import customtkinter as ctk

from snap_sweep.snap_sweep_app import SnapSweepApp


def main():

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

    SnapSweepApp(root)

    root.mainloop()


if __name__ == "__main__":
    app_env = os.getenv("APP_ENV", "development")
    print("Running in", app_env, "mode")
    if app_env != "production":
        from hupper import start_reloader

        reloader = start_reloader("snap_sweep.__main__.main")
    main()
