import tkinter
from PIL import Image
import customtkinter as ctk
import threading
import queue


class DuplicatePreviewWidget(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.duplicates = []
        self.image_queue = queue.Queue()
        self.setup_ui()
        self.bind("<MouseWheel>", self.on_mouse_wheel)

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(height=len(self.duplicates) * 64 + 100)

        # Start a thread to load images
        threading.Thread(target=self.load_images_in_thread, daemon=True).start()

        # Poll the queue to add loaded images to the UI
        self.after(100, self.process_image_queue)

    def on_mouse_wheel(self, event: tkinter.Event):
        self._parent_canvas.yview_scroll(-1 * event.delta, "units")

    def load_images_in_thread(self):
        for i, duplicate in enumerate(self.duplicates):
            self.add_duplicate_lazy(duplicate, i)

    def add_duplicate_lazy(self, duplicate: tuple[str, str, float, float, float], i):
        best_image = Image.open(duplicate[0])
        worst_image = Image.open(duplicate[1])

        best_image.thumbnail((256, 256))
        worst_image.thumbnail((256, 256))

        left_image_size = best_image.size
        right_image_size = worst_image.size

        image_left = ctk.CTkImage(light_image=best_image, size=left_image_size)
        image_right = ctk.CTkImage(light_image=worst_image, size=right_image_size)

        # Put the images into the queue
        self.image_queue.put((i, image_left, image_right))

    def process_image_queue(self):
        try:
            while not self.image_queue.empty():
                i, image_left, image_right = self.image_queue.get_nowait()

                left_label = ctk.CTkLabel(master=self, image=image_left, text=None)
                left_label.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

                right_label = ctk.CTkLabel(master=self, image=image_right, text=None)
                right_label.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        except queue.Empty:
            pass
        finally:
            # Continue polling the queue
            self.after(100, self.process_image_queue)

    def set_duplicates(self, duplicates: list[tuple[str, str, float, float, float]]):
        self.duplicates = duplicates
        self.setup_ui()
