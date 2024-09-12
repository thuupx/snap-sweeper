import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from functools import lru_cache
from shutil import copyfile, move

from filetype import is_image


def chunkify(lst, chunk_size=20):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


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
def list_all_files(directory: str, include_subdirs: bool = True) -> list[str]:
    """
    Recursively list all files in the given directory.

    Args:
        directory (str): The directory to scan.
        include_subdirs (bool): If True, scan subdirectories. If False, only scan the top-level directory.

    Returns:
        list[str]: A list of file paths.
    """
    file_list = []
    if include_subdirs:
        for root, _dirs, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                file_list.append(file_path)
    return file_list


async def get_image_files(img_folder: str, include_subdirs: bool = True) -> list[str]:
    """Asynchronously list all image files in the given directory."""

    print("Listing all files...")
    loop = asyncio.get_event_loop()
    all_files = await loop.run_in_executor(
        None, list_all_files, img_folder, include_subdirs
    )

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


async def calculate_file_hash(file_path: str) -> dict[str, str]:
    """
    Calculate the hash of a file's contents asynchronously.

    Parameters:
        file_path (str): The path to the file.
    """

    def _hash_file():
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                hasher.update(chunk)
        return {"path": file_path, "hash": hasher.hexdigest()}

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _hash_file)


async def calculate_file_hashes(file_paths: list[str], max_workers: int | None = None):
    """
    Calculate the hash of files asynchronously.

    Parameters:
        file_paths (list[str]): The paths to the files.
        max_workers (int | None): Maximum number of worker threads.

    Returns:
        dict[str, str]: A dictionary with the file paths as keys and the hashes as values.
    """
    max_workers = max_workers or (os.cpu_count() or 4) * 2

    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(executor, calculate_file_hash, file_path)
            for file_path in file_paths
        ]
        hashed_results = await asyncio.gather(*tasks)
        for coroutine in hashed_results:
            result = await coroutine
            results[result["path"]] = result["hash"]
    return results
