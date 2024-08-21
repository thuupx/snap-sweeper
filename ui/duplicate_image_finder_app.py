import asyncio
import threading
import tkinter.filedialog
import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from typing import Optional

from find_duplicate_images.handler import find_and_move_duplicates_handler


class DuplicateImageFinderApp:
    def __init__(self, root: Tk):
        self.root: Tk = root
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.image_dir: Optional[str] = None

        self.btn_process: Optional[Button] = None
        self.progress_bar: Optional[ttk.Progressbar] = None

        self.setup_ui()
        self.start_asyncio_event_loop()

    def setup_ui(self) -> None:
        self.root.title("Find Duplicate Images")
        self.root.geometry("768x576")

        top_frame: Frame = Frame(master=self.root)
        top_frame.pack(pady=20)

        bottom_frame: Frame = Frame(master=self.root)
        bottom_frame.pack(side=BOTTOM, pady=20)

        label: Label = Label(master=top_frame, text="UiTest")
        label.pack(pady=12, padx=10)

        btn_select_dir: Button = Button(
            master=top_frame, text="Select Folder", command=self.select_dir
        )
        btn_select_dir.pack(pady=12, padx=10)

        self.btn_process = Button(
            master=bottom_frame,
            text="Process",
            command=self.on_process_click,
        )
        self.btn_process.pack(pady=12, padx=10)
        self.btn_process.config(state=DISABLED)

        self.progress_bar = ttk.Progressbar(
            self.root,
            orient=HORIZONTAL,
            takefocus=True,
            mode="indeterminate",
        )

        self.progress_bar.pack()

    def select_dir(self) -> None:
        self.image_dir = tkinter.filedialog.askdirectory()
        print("Selected dir:", self.image_dir)
        if self.image_dir:
            self.btn_process.config(state=NORMAL)

    async def process_images(self) -> None:
        print("Start processing", self.image_dir)
        self.btn_process.config(state=DISABLED)
        self.progress_bar.start()

        try:
            results, error = await find_and_move_duplicates_handler(self.image_dir)
            if error:
                tkinter.messagebox.showerror("Error", error)
            else:
                print(results)
        finally:
            self.progress_bar.stop()
            self.btn_process.config(state=NORMAL)

    def on_process_click(self) -> None:
        asyncio.run_coroutine_threadsafe(self.process_images(), self.loop)

    def start_asyncio_event_loop(self) -> None:
        t = threading.Thread(
            target=self._start_event_loop, args=(self.loop,), daemon=True
        )
        t.start()

    def _start_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()
