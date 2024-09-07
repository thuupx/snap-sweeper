import os

import customtkinter as ctk

from snap_sweep.snap_sweep_app import SnapSweepApp


def main():

    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme(
        os.path.join(os.path.dirname(__file__), "themes", "sky.json")
    )

    root = ctk.CTk()
    SnapSweepApp(root)
    root.mainloop()


if __name__ == "__main__":
    app_env = os.getenv("APP_ENV", "development")
    print("Running in", app_env, "mode")
    if app_env != "production":
        from hupper import start_reloader

        reloader = start_reloader("snap_sweep.__main__.main")
    main()
