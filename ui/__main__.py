import asyncio
import threading
from tkinter import *
import tkinter
import tkinter.filedialog
from tkinter import ttk
import torch

from find_duplicate_images.compare_image_quality import analyze_pairs
from find_duplicate_images.process_images import (
    find_near_duplicates,
    get_image_pairs,
    load_embeddings,
)


def test():
    print("Hello!")


def select_dir():
    global IMAGE_DIR
    IMAGE_DIR = tkinter.filedialog.askdirectory()
    print("Selected dir:", IMAGE_DIR)
    if IMAGE_DIR:
        btn_process.config(state=tkinter.NORMAL)


async def start_processing():
    print("Start processing", IMAGE_DIR)
    progress_bar.start()
    btn_process.config(state=tkinter.DISABLED)
    device = torch.device(
        "mps"
        if torch.backends.mps.is_built()
        else "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"Using device: {device}")
    embedding, img_names = load_embeddings(
        img_folder=IMAGE_DIR, embedding_file="imgs_embedding.pkl", device=device
    )
    if embedding is None:
        tkinter.messagebox.showerror("Error", "No embeddings found or loaded.")
        return

    print(embedding.shape)
    near_duplicates = find_near_duplicates(embedding, threshold=1, top_k=5)[:10]
    img_pairs = get_image_pairs(near_duplicates, img_names)

    results = await analyze_pairs(
        img_pairs,
    )
    progress_bar.stop()


def createUI():
    global btn_process, progress_bar

    root = Tk()
    root.geometry("768x576")

    top_frame = tkinter.Frame(master=root)
    top_frame.pack(pady=20)

    bottom_frame = tkinter.Frame(master=root)
    bottom_frame.pack(side=tkinter.BOTTOM, pady=20)

    label = tkinter.Label(master=top_frame, text="UiTest")
    label.pack(pady=12, padx=10)

    btn_select_dir = tkinter.Button(
        master=top_frame, text="Select Folder", command=select_dir
    )
    btn_select_dir.pack(pady=12, padx=10)

    btn_process = tkinter.Button(
        master=bottom_frame,
        text="Process",
        command=lambda: threading.Thread(
            target=lambda: asyncio.run_coroutine_threadsafe(start_processing(), loop)
        ).start(),
    )
    btn_process.pack(pady=12, padx=10)
    btn_process.config(state=tkinter.DISABLED)

    progress_bar = ttk.Progressbar(master=bottom_frame, mode="determinate")
    progress_bar.pack(pady=12, padx=10, fill="x")
    progress_bar.config(maximum=100, value=0)
    progress_bar.start()

    root.mainloop()


def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Setup the asyncio event loop in a separate thread
loop = asyncio.new_event_loop()
t = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
t.start()

# Call the createUI function to set up and start the UI
createUI()
