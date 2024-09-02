import asyncio
import threading
import tkinter
import tkinter.dnd
from tkinter import StringVar, filedialog, messagebox
from typing import Optional, Dict, Any, Tuple, List

import customtkinter as ctk

from desktop_ui.widgets.duplicate_preview import DuplicatePreviewWidget
from desktop_ui.widgets.output import OutputWidget
from desktop_ui.widgets.select_folder import SelectFolderWidget
from desktop_ui.widgets.settings import SettingsWidget
from find_duplicate_images.core.find_and_move_similar_images import (
    find_and_move_similar_images,
)


class DuplicateImageFinderApp:
    def __init__(self, root: ctk.CTk):
        self.root: ctk.CTk = root
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

        self.btn_scan: Optional[ctk.CTkButton] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None

        self.select_folder_widget: Optional[SelectFolderWidget] = None
        self.settings_widget: Optional[SettingsWidget] = None
        self.output_widget: Optional[OutputWidget] = None
        self.preview_widget: Optional[DuplicatePreviewWidget] = None

        self.setup_ui()
        self.start_asyncio_event_loop()


    def setup_ui(self) -> None:
        self.root.title("Find Duplicate Images")
        self.root.geometry("1600x1024")

        # Configure the grid system
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # Create left frame
        left_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Create right frame
        right_frame = ctk.CTkFrame(master=self.root, corner_radius=10)
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")

        self.select_folder_widget = SelectFolderWidget(
            master=right_frame,
            cursor="pointinghand"
        )
        self.select_folder_widget.pack(
            side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10
        )
        self.select_folder_widget.image_dir.trace_add("write", self.on_image_dir_changed)

        self.settings_widget = SettingsWidget(master=right_frame)
        self.settings_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.output_widget = OutputWidget(master=right_frame)
        self.output_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.preview_widget = DuplicatePreviewWidget(master=left_frame)

        self.btn_scan = ctk.CTkButton(
            master=right_frame,
            text="Scan",
            command=self.on_btn_process_clicked,
            cursor="pointinghand"
        )
        self.btn_scan.configure(state=ctk.DISABLED)
        self.btn_scan.pack(side=tkinter.BOTTOM, padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(
            master=left_frame,
            orientation="horizontal",
            mode="indeterminate",
        )

    def on_image_dir_changed(self, *args: Any) -> None:
        value = self.select_folder_widget.image_dir.get()
        if value:
            self.btn_scan.configure(state=ctk.NORMAL)
        else:
            self.btn_scan.configure(state=ctk.DISABLED)

    def on_btn_process_clicked(self) -> None:
        self.btn_scan.configure(state=ctk.DISABLED)
        self.progress_bar.pack(side=tkinter.BOTTOM, fill="x", padx=8, pady=8)
        self.progress_bar.start()
        if not self.loop.is_running():
            self.start_asyncio_event_loop()
        asyncio.run_coroutine_threadsafe(self.process_images(), self.loop)

    async def process_images(self) -> None:
        try:
            settings = self.settings_widget.get_settings()
            image_dir = self.select_folder_widget.image_dir.get()
            print("Start process with settings:", settings)
            results, error = await find_and_move_similar_images(
                image_dir,
                dry_run=True,
                top_k=int(settings["top_k"]),
                threshold=int(settings["threshold"]) / 100,
                sub_folder_name=str(settings["sub_folder_name"]),
            )
            if error:
                messagebox.showerror("Error", error)
            elif results:
                self.preview_widget.set_duplicates(results)
                self.preview_widget.pack(
                    side=tkinter.TOP, fill=tkinter.BOTH, padx=10, pady=10
                )
            else:
                messagebox.showerror("Error", "Error: No results found.")

        except Exception as e:
            print(e)
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
