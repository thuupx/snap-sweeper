import os
from tkinter import StringVar, filedialog
from typing_extensions import Any
import customtkinter as ctk


class SelectFolderWidget(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, corner_radius=10, **kwargs)
        self.image_dir: StringVar = StringVar()
        self.image_dir.trace_add("write", self.on_image_dir_changed)

        self.setup_ui()

    def setup_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        self.text_label = ctk.CTkLabel(
            master=self,
            height=64,
            text=self.image_dir.get() or "Select Folder",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.text_label.bind("<Button-1>", self.on_btn_select_dir_clicked)
        self.text_label.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="ew")

    def set_text(self, text: str) -> None:
        if os.path.exists(text):
            if len(text) > 50:
                text = ".../" + text.rsplit("/", 1)[-1]
        self.text_label.configure(text=text)

    def on_btn_select_dir_clicked(self, event) -> None:
        directory = filedialog.askdirectory(
            title="Select Images Folder", initialdir=self.image_dir.get()
        )
        if directory:
            self.image_dir.set(directory)

    def on_image_dir_changed(self, *args: Any) -> None:
        if self.image_dir.get():
            self.set_text(self.image_dir.get())
