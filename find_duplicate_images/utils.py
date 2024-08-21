import os
from functools import lru_cache
from multiprocessing import Pool, cpu_count

import cv2

HASH_FILE = "dir_hash.json"


def chunkify(lst, chunk_size=20):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


@lru_cache(maxsize=None)
def memorize_imread(filepath, flags=cv2.IMREAD_COLOR):
    """
    Reads an image from a file using OpenCV, with memoization.
    """
    return cv2.imread(filepath, flags)


def copy_file(file_path: str, dest_folder: str):
    import os
    from distutils.file_util import copy_file as _copy_file

    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if os.path.exists(dest_path):
        print(f"File {file_path} already exists, skipping.")
        return
    _copy_file(file_path, dest_path)


def move_file(file_path: str, dest_folder: str):
    import os
    from distutils.file_util import move_file as _move_file

    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if os.path.exists(dest_path):
        print(f"File {file_path} already exists, skipping.")
        return
    _move_file(file_path, dest_path)


def is_image_file(file_path: str) -> bool:
    """Check if the given file is an image file."""
    try:
        # Attempt to read the image file using OpenCV
        img = cv2.imread(file_path)
        # Check if the result is None (i.e., cv2 couldn't read the file as an image)
        return img is not None
    except Exception:
        return False


def list_all_files(folder: str) -> list[str]:
    """List all files in the given directory."""
    # List all files in the directory using os.scandir
    with os.scandir(folder) as entries:
        return [entry.path for entry in entries if entry.is_file()]


def get_image_files(img_folder: str) -> list[str]:
    """List all image files in the given directory."""

    print("Listing all files...")
    all_files = list_all_files(img_folder)

    # Create a multiprocessing pool
    with Pool(cpu_count()) as pool:
        img_validity = pool.map(is_image_file, all_files)

    # Filter and collect valid image files
    valid_img_files = [file for file, valid in zip(all_files, img_validity) if valid]

    # Sort the image file paths
    valid_img_files.sort()

    return valid_img_files
