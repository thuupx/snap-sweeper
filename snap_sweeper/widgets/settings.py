from tkinter import BooleanVar, IntVar, StringVar

import customtkinter as ctk


class SettingsWidget(ctk.CTkFrame):
    def __init__(self, *args, master: ctk.CTkFrame, **kwargs):
        super().__init__(*args, master=master, corner_radius=10, **kwargs)
        self.master = master
        self.threshold = IntVar(value=95)
        self.top_k = IntVar(value=2)
        self.should_move_images = BooleanVar(value=False)
        self.sub_folder_name = StringVar(value="LOW_QUALITY_IMAGES")
        self.image_thumbnail_size = IntVar(value=512)
        self.include_subdirs = BooleanVar(value=False)

        self.should_move_images.trace_add("write", self.on_dry_run_changed)
        self.setup_ui()

    def setup_ui(self):
        # set up grid system
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=4)

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
            text="Similar ratio:",
        )
        self.threshold_value_label = ctk.CTkLabel(
            master=self,
            text=f"{self.threshold.get():.1f}%",
            width=64,
        )
        self.threshold_label.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
            columnspan=2,
        )
        self.threshold_value_label.grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.threshold_slider.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Top-k input and label
        self.top_k_label = ctk.CTkLabel(master=self, text="Top-k:")
        self.top_k_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.top_k_input = ctk.CTkEntry(master=self, textvariable=self.top_k, width=170)
        self.top_k_input.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # sub folder name input and label
        self.sub_folder_name_label = ctk.CTkLabel(
            master=self, text="Temporary trash folder name:"
        )
        self.sub_folder_name_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.sub_folder_name_input = ctk.CTkEntry(
            master=self, textvariable=self.sub_folder_name, width=170
        )
        self.sub_folder_name_input.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        # Image thumbnail input and label
        self.image_thumbnail_label = ctk.CTkLabel(
            master=self, text="Preview image size (px):"
        )
        self.image_thumbnail_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.image_thumbnail_input = ctk.CTkEntry(
            master=self,
            textvariable=self.image_thumbnail_size,
            width=170,
        )
        self.image_thumbnail_input.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        description_text = "Reduce the size if you are experiencing performance issues."

        self.description_text = ctk.CTkLabel(
            master=self,
            text=description_text,
            text_color="grey",
            anchor="w",
            width=200,
            font=ctk.CTkFont(size=12, slant="italic"),
        )
        self.description_text.grid(
            row=4,
            column=1,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="w",
        )
        # checkbox to dertermine if we want to move the images or not
        self.include_subdirs_checkbox = ctk.CTkCheckBox(
            master=self,
            text="",
            variable=self.include_subdirs,
            onvalue=True,
            offvalue=False,
        )
        self.include_subdirs_checkbox.grid(row=5, column=2, padx=5, pady=5, sticky="w")

        self.include_subdirs_checkbox_label = ctk.CTkLabel(
            master=self, text="Scan all subdirectories"
        )
        self.include_subdirs_checkbox_label.grid(
            row=5, column=1, padx=5, pady=5, sticky="w"
        )

    def on_threshold_changed(self, *args) -> None:
        self.threshold_value_label.configure(text=f"{self.threshold.get():.1f}%")

    def on_dry_run_changed(self, *args) -> None:
        if self.should_move_images.get():
            input_state = ctk.NORMAL
            text = "Low quality images will be moved to temporary folder inside the image folder."
        else:
            input_state = ctk.DISABLED
            text = "Dry run mode enabled, skipping image move."
        self.sub_folder_name_input.configure(state=input_state)
        self.description_text.configure(text=text)

    def get_settings(self):
        return {
            "threshold": self.threshold.get() / 100,
            "top_k": self.top_k.get(),
            "dry_run": not self.should_move_images.get(),
            "sub_folder_name": self.sub_folder_name.get(),
            "thumbnail_size": self.image_thumbnail_size.get(),
            "include_subdirs": self.include_subdirs.get(),
        }

    def set_thumbnail_size(self, size: int):
        self.image_thumbnail_size.set(size)
