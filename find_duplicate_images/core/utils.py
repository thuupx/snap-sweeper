import asyncio
import os
from functools import lru_cache
from shutil import copyfile, move
from filetype import is_image


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


async def is_image_file(file_path: str) -> bool:
    try:
        loop = asyncio.get_event_loop()
        is_image_obj = await loop.run_in_executor(None, is_image, file_path)
        return is_image_obj
    except Exception:
        return False


@lru_cache(maxsize=None)
def list_all_files(directory: str) -> list[str]:
    """Recursively list all files in the given directory."""
    file_list = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


async def get_image_files(img_folder: str) -> list[str]:
    """Asynchronously list all image files in the given directory."""

    print("Listing all files...")
    loop = asyncio.get_event_loop()
    all_files = await loop.run_in_executor(None, list_all_files, img_folder)

    # Create tasks for checking each file asynchronously
    tasks = [is_image_file(file) for file in all_files]
    img_validity = await asyncio.gather(*tasks)

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
