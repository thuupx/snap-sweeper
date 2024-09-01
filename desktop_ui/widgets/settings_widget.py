from tkinter import Variable
import customtkinter as ctk


class SettingsWidget(ctk.CTkFrame):
    def __init__(self, *args, master, **kwargs):
        super().__init__(*args, master=master, corner_radius=10, **kwargs)
        self.master = master
        self.threshold = Variable(value=90)
        self.top_k = Variable(value=2)
        self.move_images = Variable(value=True)
        self.setup_ui()

    def setup_ui(self):
        # set up grid system
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.threshold_slider = ctk.CTkSlider(
            master=self,
            command=self.on_threshold_changed,
            from_=50,
            to=100,
            number_of_steps=100,
            width=200,
            height=20,
            variable=self.threshold,
        )
        self.threshold_label = ctk.CTkLabel(
            master=self,
            width=128,
            text=f"Similar ratio: {self.threshold.get()}%",
        )
        self.threshold_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.threshold_slider.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Top-k input and label
        self.top_k_label = ctk.CTkLabel(master=self, text="Top-k:")
        self.top_k_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.top_k_input = ctk.CTkEntry(master=self, width=64, textvariable=self.top_k)
        self.top_k_input.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # checkbox to dertermine if we want to move the images or not
        self.move_images_checkbox = ctk.CTkCheckBox(
            master=self,
            text=None,
            variable=self.move_images,
            onvalue=True,
            offvalue=False,
        )
        self.move_images_checkbox_label = ctk.CTkLabel(
            master=self, text="Move images to sub folder:"
        )
        self.move_images_checkbox_label.grid(
            row=2, column=1, padx=5, pady=5, sticky="w"
        )
        self.move_images_checkbox.grid(row=2, column=2, padx=5, pady=5, sticky="w")

    def on_threshold_changed(self, *args):
        self.threshold_label.configure(
            text=f"Similar ratio: {float(self.threshold.get())}%"
        )
