import ctypes


def set_app_id(app_id):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)  # type: ignore


if __name__ == "__main__":
    set_app_id("Snap Sweeper")
