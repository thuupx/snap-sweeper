import tkinter
import customtkinter as ctk
from .widgets.duplicate_preview import DuplicatePreviewWidget
from .widgets.output import OutputWidget
from .widgets.select_folder import SelectFolderWidget
from .widgets.settings import SettingsWidget


class UIManager:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.btn_scan: ctk.CTkButton
        self.sweep_button: ctk.CTkButton
        self.progress_bar: ctk.CTkProgressBar
        self.select_folder_widget: SelectFolderWidget
        self.settings_widget: SettingsWidget
        self.output_widget: OutputWidget
        self.preview_widget: DuplicatePreviewWidget

    def setup_ui(self):
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

        self.settings_widget = SettingsWidget(master=right_frame)
        self.settings_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.output_widget = OutputWidget(master=right_frame)
        self.output_widget.pack(side=tkinter.TOP, fill=tkinter.X, padx=10, pady=10)

        self.preview_widget = DuplicatePreviewWidget(
            master=left_frame,
            custom_thumbnail_size=self.settings_widget.image_thumbnail_size.get(),
        )
        self.settings_widget.image_thumbnail_size.trace_add(
            "write",
            lambda *args: self.preview_widget.set_thumbnail_size(
                self.settings_widget.image_thumbnail_size.get()
            ),
        )

        self.sweep_button = ctk.CTkButton(
            right_frame,
            text="Start Sweep",
            fg_color="#ef4444",
            hover_color="#dc2626",
        )
        self.sweep_button.configure(state=ctk.DISABLED)
        self.sweep_button.pack(side=ctk.BOTTOM, padx=10, pady=(0, 10))

        self.btn_scan = ctk.CTkButton(
            master=right_frame,
            text="Scan",
        )
        self.btn_scan.configure(state=ctk.DISABLED)
        self.btn_scan.pack(side=tkinter.BOTTOM, padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(
            master=left_frame,
            orientation="horizontal",
            mode="indeterminate",
        )

    def start_processing(self):
        self.btn_scan.configure(state=ctk.DISABLED)
        self.progress_bar.pack(side=ctk.BOTTOM, fill="x", padx=8, pady=8)
        self.progress_bar.start()
        self.output_widget.clear()

    def finish_processing(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_scan.configure(state=ctk.NORMAL)
        self.sweep_button.configure(state=ctk.NORMAL)
