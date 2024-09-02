import sys
import customtkinter as ctk


class OutputWidget(ctk.CTkFrame):
    def __init__(self, *args, master, **kwargs):
        super().__init__(*args, master=master, corner_radius=10, **kwargs)
        self.master = master
        self.setup_ui()

        # Redirect stdout to this widget
        self.stdout = self.CustomStream(self.output_text)
        sys.stdout = self.stdout

    class CustomStream:
        def __init__(self, text_widget: ctk.CTkTextbox):
            self.text_widget = text_widget

        def write(self, message: str):
            self.text_widget.configure(state=ctk.NORMAL)
            self.text_widget.insert(ctk.END, message)
            self.text_widget.configure(state=ctk.DISABLED)
            # Autoscroll to the bottom
            self.text_widget.yview(ctk.END)

        def flush(self):
            pass

    def setup_ui(self):
        # set up grid system
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.output_label = ctk.CTkLabel(
            master=self,
            text="Debug Output",
        )
        self.output_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.output_text = ctk.CTkTextbox(
            master=self,
        )
        self.output_text.configure(state=ctk.DISABLED)
        self.output_text.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    def clear(self):
        self.output_text.configure(state=ctk.NORMAL)
        self.output_text.delete(0.0, ctk.END)
        self.output_text.configure(state=ctk.DISABLED)
