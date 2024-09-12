import queue
import threading
from typing import Any

import customtkinter as ctk
from PIL import Image, ImageOps

CHUNK_SIZE = 10  # Number of images to load per chunk
LOAD_MORE_BUTTON_TEXT = "Load More"


class DuplicatePreviewWidget(ctk.CTkScrollableFrame):
    def __init__(self, master: ctk.CTkFrame, custom_thumbnail_size: int = 512):
        super().__init__(master)
        self.master = master
        self.master.anchor(ctk.CENTER)
        self.duplicates = []
        self.image_queue = queue.Queue()
        self.current_chunk = 0
        self.total_items = 0
        self.custom_thumbnail_size = custom_thumbnail_size
        self.setup_ui()
        self.bind("<MouseWheel>", self.on_mouse_wheel)

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(height=self.master.winfo_height())
        self._parent_canvas.yview_moveto(0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # Add labels for "Best Image" and "Worst Image"
        best_label = ctk.CTkLabel(
            self, text="High quality images", font=("Arial", 16, "bold")
        )
        best_label.grid(row=0, column=0, padx=5, pady=(5, 10))

        worst_label = ctk.CTkLabel(
            self, text="Low quality images", font=("Arial", 16, "bold")
        )
        worst_label.grid(row=0, column=1, padx=5, pady=(5, 10))

        # Reset chunk
        self.current_chunk = 0
        self.total_items = len(self.duplicates)

        # Load initial chunk of images
        self.load_next_chunk()

    def on_mouse_wheel(self, event: Any):
        self._parent_canvas.yview_scroll(-1 * event.delta, "units")

    def load_images_in_thread(self, start_index):
        end_index = min(start_index + CHUNK_SIZE, self.total_items)
        for i in range(start_index, end_index):
            duplicate = self.duplicates[i]
            self.add_duplicate_lazy(duplicate, i)
        self.image_queue.put("done")

    def add_duplicate_lazy(
        self, duplicate: tuple[str, str, float, float, float], i: int
    ):
        best_image = Image.open(duplicate[0])
        worst_image = Image.open(duplicate[1])

        thumbnail_size = 512
        padding = 10 * 2
        master = self.master
        width = master.winfo_width()
        height = master.winfo_height()
        scrollbar_width = self._scrollbar.winfo_width()
        if width > height:
            thumbnail_size = width // 2 - padding - scrollbar_width
        else:
            thumbnail_size = height // 2 - padding - scrollbar_width

        thumbnail_size = min(thumbnail_size, self.custom_thumbnail_size, 512)

        best_image = ImageOps.exif_transpose(best_image) or best_image
        worst_image = ImageOps.exif_transpose(worst_image) or worst_image

        best_image.thumbnail((thumbnail_size, thumbnail_size))
        worst_image.thumbnail((thumbnail_size, thumbnail_size))

        left_image_size = best_image.size
        right_image_size = worst_image.size

        image_left = ctk.CTkImage(
            light_image=best_image, dark_image=best_image, size=left_image_size
        )
        image_right = ctk.CTkImage(
            light_image=worst_image, dark_image=worst_image, size=right_image_size
        )

        # Put the images into the queue
        self.image_queue.put((i, image_left, image_right))

    def process_image_queue(self):
        try:
            while not self.image_queue.empty():
                item = self.image_queue.get_nowait()
                if item == "done":
                    self.add_load_more_button()
                    continue

                i, image_left, image_right = item

                self.left_label = ctk.CTkLabel(
                    master=self, image=image_left, text="", cursor="pointinghand"
                )
                self.left_label.bind(
                    "<Button-1>",
                    lambda event: self.on_image_clicked(event, image_left),
                )
                self.left_label.grid(row=i + 1, column=0, padx=5, pady=5)

                self.right_label = ctk.CTkLabel(
                    master=self, image=image_right, text="", cursor="pointinghand"
                )
                self.right_label.bind(
                    "<Button-1>",
                    lambda event: self.on_image_clicked(event, image_right),
                )
                self.right_label.grid(row=i + 1, column=1, padx=5, pady=5)
        except queue.Empty:
            pass
        finally:
            # Continue polling the queue
            self.after(100, self.process_image_queue)

    def set_duplicates(self, duplicates: list[tuple[str, str, float, float, float]]):
        self.duplicates = duplicates
        self.setup_ui()

    def load_next_chunk(self):
        start_index = self.current_chunk * CHUNK_SIZE
        threading.Thread(
            target=self.load_images_in_thread, args=(start_index,), daemon=True
        ).start()
        self.current_chunk += 1
        self.after(100, self.process_image_queue)
        # Remove the existing "Load More" button
        for widget in self.winfo_children():
            if (
                isinstance(widget, ctk.CTkButton)
                and widget.cget("text") == LOAD_MORE_BUTTON_TEXT
            ):
                widget.destroy()

    def add_load_more_button(self):
        if self.current_chunk * CHUNK_SIZE >= self.total_items:
            return

        load_more_button = ctk.CTkButton(
            master=self,
            text=LOAD_MORE_BUTTON_TEXT,
            command=self.load_next_chunk,
            width=200,
        )
        load_more_button.grid(
            row=self.current_chunk * CHUNK_SIZE + 1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
        )

    def on_image_clicked(self, event: Any, ctk_image: ctk.CTkImage):
        image: Image.Image = ctk_image.cget("light_image")
        image.show()

    def set_thumbnail_size(self, size: int):
        self.custom_thumbnail_size = size
