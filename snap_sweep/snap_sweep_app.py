import asyncio
import threading
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from .snap_sweeper import SnapSweeper
from .ui_manager import UIManager


class SnapSweepApp:
    def __init__(self, root: ctk.CTk):
        self.root: ctk.CTk = root
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.ui_manager: UIManager = UIManager(root)
        self.sweeper: SnapSweeper = SnapSweeper()

    def setup_ui(self) -> None:
        self.ui_manager.setup_ui()
        self.ui_manager.select_folder_widget.image_dir.trace_add(
            "write", self.on_image_dir_changed
        )
        self.ui_manager.btn_scan.configure(command=self.on_btn_process_clicked)
        self.ui_manager.sweep_button.configure(command=self.on_sweep_clicked)

    def on_image_dir_changed(self, *args: Any) -> None:
        value = self.ui_manager.select_folder_widget.image_dir.get()
        self.ui_manager.btn_scan.configure(state=ctk.NORMAL if value else ctk.DISABLED)

    def on_btn_process_clicked(self) -> None:
        self.ui_manager.start_processing()
        asyncio.run_coroutine_threadsafe(self.process_images(), self.loop)

    def on_sweep_clicked(self) -> None:
        asyncio.run_coroutine_threadsafe(self.start_sweep(), self.loop)

    async def process_images(self) -> None:
        try:
            settings = self.ui_manager.settings_widget.get_settings()
            image_dir = self.ui_manager.select_folder_widget.image_dir.get()
            results, discarded_images, error = await self.sweeper.process_images(
                image_dir, settings
            )
            self.handle_processing_results(results, discarded_images, error)
        except Exception as e:
            self.handle_processing_error(e)
        finally:
            self.ui_manager.finish_processing()

    def handle_processing_results(self, results, discarded_images, error):
        if error:
            messagebox.showerror("Error", error)
        elif results and discarded_images:
            self.ui_manager.preview_widget.set_duplicates(results)
            self.ui_manager.preview_widget.pack(
                side=ctk.TOP, fill=ctk.BOTH, padx=10, pady=10
            )
            self.sweeper.discarded_images = discarded_images
            self.ui_manager.sweep_button.configure(state=ctk.NORMAL)
        else:
            messagebox.showerror("Error", "Error: No results found.")

    def handle_processing_error(self, error):
        print(error)
        messagebox.showerror("Error", str(error))

    async def start_sweep(self) -> None:
        if self.confirm_sweep():
            await self.perform_sweep()
        else:
            self.cancel_sweep()

    def confirm_sweep(self) -> bool:
        return (
            messagebox.askyesno(
                "Confirmation", "Are you sure you want to start the sweep?"
            )
            and len(self.sweeper.discarded_images) > 0
        )

    async def perform_sweep(self) -> None:
        settings = self.ui_manager.settings_widget.get_settings()
        await self.sweeper.move_discarded_images(settings["sub_folder_name"])
        self.ui_manager.sweep_button.configure(state=ctk.DISABLED)

    def cancel_sweep(self) -> None:
        self.ui_manager.sweep_button.configure(state=ctk.NORMAL)
        self.ui_manager.btn_scan.configure(state=ctk.NORMAL)

    def setup_event_loop(self) -> None:
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
