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
