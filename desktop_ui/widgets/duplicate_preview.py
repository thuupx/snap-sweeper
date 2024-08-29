from PIL import Image
import customtkinter as ctk


class DuplicatePreviewWidget(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.duplicates = []

        self.configure_ui()
        self.setup_ui()

    def configure_ui(self):
        # General configuration of the grid and appearance
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(height=len(self.duplicates) * 64 + 100)

        for i, duplicate in enumerate(self.duplicates):
            self.add_duplicate(duplicate, i)

    def add_duplicate(self, duplicate: tuple[str, str, float, float, float], i: int):
        # Open images
        best_image = Image.open(duplicate[0])
        worst_image = Image.open(duplicate[1])

        # Create thumbnails
        best_image.thumbnail((256, 256))
        worst_image.thumbnail((256, 256))

        # Create image objects for labels
        image_left = ctk.CTkImage(light_image=best_image, size=best_image.size)
        image_right = ctk.CTkImage(light_image=worst_image, size=worst_image.size)

        # Create and place labels
        left_label = ctk.CTkLabel(master=self, image=image_left, text=None)
        left_label.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
        right_label = ctk.CTkLabel(master=self, image=image_right, text=None)
        right_label.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

    def set_duplicates(self, duplicates):
        self.duplicates = duplicates
        self.setup_ui()
