import os


def main():
    from desktop_ui.duplicate_image_finder_app import DuplicateImageFinderApp
    import customtkinter as ctk
    import os

    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme(
        os.path.join(os.path.dirname(__file__), "themes", "sky.json")
    )

    root = ctk.CTk()
    app = DuplicateImageFinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    app_env = os.getenv("APP_ENV", "development")
    print("Running in", app_env, "mode")
    if app_env != "production":
        from hupper import start_reloader

        reloader = start_reloader("desktop_ui.__main__.main")
    main()
