import asyncio
import threading
from tkinter import filedialog, messagebox, StringVar
import tkinter
import tkinter.dnd
from typing import Optional

import customtkinter as ctk

from find_duplicate_images.handler import find_and_move_duplicates_handler
from ui.widgets.select_folder import SelectFolderWidget


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
        self.root.geometry("1024x768")

        # Configure the grid system
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)

        # Create left frame
        left_frame = ctk.CTkFrame(master=self.root, corner_radius=10)
        left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")

        # Create right frame
        right_frame = ctk.CTkFrame(master=self.root, corner_radius=10)
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")

        self.setting_widget = SelectFolderWidget(
            master=right_frame,
            text_variable=self.image_dir.get() or "Select Folder",
            on_text_click=self.on_btn_select_dir_clicked,
            cursor="pointinghand",
        )
        self.setting_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.btn_scan = ctk.CTkButton(
            master=right_frame,
            text="Scan",
            command=self.on_btn_process_clicked,
        )
        self.btn_scan.pack(side=tkinter.BOTTOM, padx=10, pady=10)
        self.btn_scan.configure(state=ctk.DISABLED)

        self.progress_bar = ctk.CTkProgressBar(
            master=left_frame,
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
        if self.setting_widget:
            self.setting_widget.set_text(self.image_dir.get())
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
        self.progress_bar.pack(side=tkinter.BOTTOM, fill="x", padx=8, pady=8)
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
