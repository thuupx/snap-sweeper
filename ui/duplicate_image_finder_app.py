import asyncio
import threading
from tkinter import filedialog, messagebox, StringVar
from typing import Optional

import customtkinter as ctk

from find_duplicate_images.handler import find_and_move_duplicates_handler


class DuplicateImageFinderApp:
    def __init__(self, root: ctk.CTk):
        self.root: ctk.CTk = root
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.image_dir: StringVar = StringVar()

        self.btn_scan: Optional[ctk.CTkButton] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None

        self.setup_ui()
        self.start_asyncio_event_loop()

        self.image_dir.trace_add("write", self.on_image_dir_changed)

    def setup_ui(self) -> None:
        self.root.title("Find Duplicate Images")
        self.root.geometry("800x600")

        top_frame: ctk.CTkFrame = ctk.CTkFrame(master=self.root)
        top_frame.pack(pady=20)

        bottom_frame: ctk.CTkFrame = ctk.CTkFrame(master=self.root)
        bottom_frame.pack(side=ctk.BOTTOM, pady=20)

        btn_select_dir: ctk.CTkButton = ctk.CTkButton(
            master=top_frame,
            text="Select Folder",
            command=self.on_btn_select_dir_clicked,
        )
        btn_select_dir.pack()

        self.btn_scan = ctk.CTkButton(
            master=bottom_frame,
            text="Scan",
            command=self.on_btn_process_clicked,
        )
        self.btn_scan.pack()
        self.btn_scan.configure(state=ctk.DISABLED)

        self.progress_bar = ctk.CTkProgressBar(
            master=self.root,
            orientation="horizontal",
            mode="indeterminate",
        )

    def on_btn_select_dir_clicked(self) -> None:
        directory = filedialog.askdirectory(
            title="Select Images Folder", initialdir=self.image_dir.get()
        )
        if directory:
            self.image_dir.set(directory)

    def on_image_dir_changed(self, *args) -> None:
        if self.image_dir.get():
            self.btn_scan.configure(state=ctk.NORMAL)
        else:
            self.btn_scan.configure(state=ctk.DISABLED)

    def on_btn_process_clicked(self) -> None:
        if not self.loop.is_running():
            self.start_asyncio_event_loop()
        asyncio.run_coroutine_threadsafe(self.process_images(), self.loop)

    async def process_images(self) -> None:
        self.btn_scan.configure(state=ctk.DISABLED)
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.start()

        try:
            results, error = await find_and_move_duplicates_handler(
                self.image_dir.get(), dry_run=True
            )
            if error:
                messagebox.showerror("Error", error)
            else:
                print(results)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.btn_scan.configure(state=ctk.NORMAL)

    def start_asyncio_event_loop(self) -> None:
        t = threading.Thread(
            target=self._start_event_loop, args=(self.loop,), daemon=True
        )
        t.start()

    def _start_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()
