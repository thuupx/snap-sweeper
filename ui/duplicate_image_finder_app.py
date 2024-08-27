import asyncio
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional

from find_duplicate_images.handler import find_and_move_duplicates_handler


class DuplicateImageFinderApp:
    def __init__(self, root: ctk.CTk):
        self.root: ctk.CTk = root
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.image_dir: Optional[str] = None

        self.btn_process: Optional[ctk.CTkButton] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None

        self.setup_ui()
        self.start_asyncio_event_loop()

    def setup_ui(self) -> None:
        self.root.title("Find Duplicate Images")
        self.root.geometry("768x576")

        top_frame: ctk.CTkFrame = ctk.CTkFrame(master=self.root)
        top_frame.pack(pady=20)

        bottom_frame: ctk.CTkFrame = ctk.CTkFrame(master=self.root)
        bottom_frame.pack(side=ctk.BOTTOM, pady=20)

        btn_select_dir: ctk.CTkButton = ctk.CTkButton(
            master=top_frame, text="Select Folder", command=self.select_dir_handler
        )
        btn_select_dir.pack()

        self.btn_process = ctk.CTkButton(
            master=bottom_frame,
            text="Process",
            command=self.on_process_click_handler,
        )
        self.btn_process.pack()
        self.btn_process.configure(state=ctk.DISABLED)

        self.progress_bar = ctk.CTkProgressBar(
            master=self.root,
            orientation="horizontal",
            mode="indeterminate",
        )

        self.progress_bar.pack(pady=12, padx=10)

    def select_dir_handler(self) -> None:
        self.image_dir = filedialog.askdirectory()
        print("Selected dir:", self.image_dir)
        if self.image_dir:
            self.btn_process.configure(state=ctk.NORMAL)

    async def process_images(self) -> None:
        print("Start processing", self.image_dir)
        self.btn_process.configure(state=ctk.DISABLED)
        self.progress_bar.start()

        try:
            results, error = await find_and_move_duplicates_handler(self.image_dir)
            if error:
                messagebox.showerror("Error", error)
            else:
                print(results)
        except Exception as e:
            print(e)
            messagebox.showerror("Error", str(e))
        finally:
            self.progress_bar.stop()
            self.btn_process.configure(state=ctk.NORMAL)

    def on_process_click_handler(self) -> None:
        asyncio.run_coroutine_threadsafe(self.process_images(), self.loop)

    def start_asyncio_event_loop(self) -> None:
        t = threading.Thread(
            target=self._start_event_loop, args=(self.loop,), daemon=True
        )
        t.start()

    def _start_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()
