import asyncio
import os
from functools import lru_cache
from shutil import copyfile, move


def chunkify(lst, chunk_size=20):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


@lru_cache(maxsize=None)
def memorize_imread(filepath, flags=None):
    """
    Reads an image from a file using OpenCV, with memoization.
    """
    import cv2

    flags = flags or cv2.IMREAD_COLOR

    return cv2.imread(filepath, flags)


def copy_file(file_path: str, dest_folder: str):

    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if os.path.exists(dest_path):
        print(f"File {file_path} already exists, skipping.")
        return
    copyfile(file_path, dest_path)


def move_file(file_path: str, dest_folder: str):

    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if os.path.exists(dest_path):
        print(f"File {file_path} already exists, skipping.")
        return
    move(file_path, dest_path)


def is_image_file(file_path: str) -> bool:
    """Check if the given file is an image file."""
    try:
        # Attempt to read the image file using OpenCV
        img = memorize_imread(file_path)
        # Check if the result is None (i.e., cv2 couldn't read the file as an image)
        return img is not None
    except Exception:
        return False


def list_all_files(folder: str) -> list[str]:
    """List all files in the given directory."""
    import os

    # List all files in the directory using os.scandir
    with os.scandir(folder) as entries:
        return [entry.path for entry in entries if entry.is_file()]


def get_image_files(img_folder: str) -> list[str]:
    """List all image files in the given directory."""

    print("Listing all files...")
    from multiprocessing import Pool, cpu_count

    all_files = list_all_files(img_folder)

    # Create a multiprocessing pool
    with Pool(cpu_count()) as pool:
        img_validity = pool.map(is_image_file, all_files)

    # Filter and collect valid image files
    valid_img_files = [file for file, valid in zip(all_files, img_validity) if valid]

    # Sort the image file paths
    valid_img_files.sort()

    return valid_img_files


async def async_move_file_to_subdir(src: str, dest_subfolder: str):
    """
    Move a file to a specified subfolder inside its directory.

    Parameters:
        src (str): The source file path.
        dest_subfolder (str): The subfolder name within the source file's directory.
    """
    # Determine the base directory and destination path
    base_dir = os.path.dirname(src)
    dest_dir = os.path.join(base_dir, dest_subfolder)
    dest_path = os.path.join(dest_dir, os.path.basename(src))

    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Use asyncio to move the file
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, move, src, dest_path)


async def move_files_to_subdir(files: list[str], dest_subfolder: str):
    """
    Move multiple files to a specified subfolder inside their directories.

    Parameters:
        files (list[str]): List of source file paths.
        dest_subfolder (str): The subfolder name within each source file's directory.
    """
    tasks = [async_move_file_to_subdir(file, dest_subfolder) for file in files]
    await asyncio.gather(*tasks)
