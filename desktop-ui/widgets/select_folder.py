import os
import customtkinter as ctk


class SelectFolderWidget(ctk.CTkFrame):
    def __init__(self, *args, text_variable=None, on_text_click=None, **kwargs):
        super().__init__(*args, corner_radius=15, **kwargs)
        self.on_text_click = on_text_click
        self.text_variable = text_variable
        self.setup_ui()
        if self.on_text_click:
            self.text_label.bind("<Button-1>", self._on_text_click)

    def setup_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        self.text_label = ctk.CTkLabel(
            master=self,
            width=200,
            height=64,
            text=self.text_variable,
        )
        self.text_label.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="ew")

    def _on_text_click(self, event):
        self.on_text_click()

    def set_text(self, text: str) -> None:
        if os.path.exists(text):
            text = os.path.basename(text)
            if len(text) > 26:
                text = text[:23] + "..."

        self.text_label.configure(text=text)
