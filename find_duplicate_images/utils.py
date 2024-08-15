from functools import lru_cache

import cv2


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
