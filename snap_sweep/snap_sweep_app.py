import asyncio
import threading
import tkinter
from tkinter import messagebox
from typing import Any, Optional

import customtkinter as ctk

from find_duplicate_images.core.find_and_move_similar_images import (
    find_and_move_similar_images,
)
from .widgets.duplicate_preview import DuplicatePreviewWidget
from .widgets.output import OutputWidget
from .widgets.select_folder import SelectFolderWidget
from .widgets.settings import SettingsWidget


class SnapSweepApp:
    def __init__(self, root: ctk.CTk):
        self.root: ctk.CTk = root
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self.btn_scan: Optional[ctk.CTkButton] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None

        self.select_folder_widget: Optional[SelectFolderWidget] = None
        self.settings_widget: Optional[SettingsWidget] = None
        self.output_widget: Optional[OutputWidget] = None
        self.preview_widget: Optional[DuplicatePreviewWidget] = None

        self.ensure_asyncio_event_loop()

    def setup_ui(self) -> None:
        # Create left frame
        left_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Create right frame
        right_frame = ctk.CTkFrame(master=self.root, corner_radius=10)
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")

        self.select_folder_widget = SelectFolderWidget(
            master=right_frame, cursor="pointinghand"
        )
        self.select_folder_widget.pack(
            side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10
        )
        self.select_folder_widget.image_dir.trace_add(
            "write", self.on_image_dir_changed
        )

        self.settings_widget = SettingsWidget(master=right_frame)
        self.settings_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.output_widget = OutputWidget(master=right_frame)
        self.output_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.preview_widget = DuplicatePreviewWidget(master=left_frame)

        self.btn_scan = ctk.CTkButton(
            master=right_frame,
            text="Scan",
            command=self.on_btn_process_clicked,
            cursor="pointinghand",
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
        self.output_widget.clear()
        asyncio.run_coroutine_threadsafe(self.process_images(), self.loop)

    async def process_images(self) -> None:
        try:
            settings = self.settings_widget.get_settings()
            image_dir = self.select_folder_widget.image_dir.get()
            print(settings)
            results, error = await find_and_move_similar_images(
                image_dir,
                dry_run=bool(settings["dry_run"]),
                top_k=int(settings["top_k"]),
                threshold=float(settings["threshold"]),
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

    def ensure_asyncio_event_loop(self) -> None:
        if not self.loop.is_running():
            t = threading.Thread(target=self._run_event_loop, daemon=True)
            t.start()

    def _run_event_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def cleanup(self) -> None:
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
        self.loop.call_soon_threadsafe(self.loop.stop)
