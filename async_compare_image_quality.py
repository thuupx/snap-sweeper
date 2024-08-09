import cv2
import asyncio
from tqdm.asyncio import tqdm

from utils import chunkify


def compute_sharpness(image_path):
    """
    Computes the sharpness of an image using the Laplacian of Gaussian.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var


async def compare_pair(img1_path, img2_path):
    """
    Compares the sharpness of two images.

    @return: tuple of (best_img, worst_img, best_sharpness, worst_sharpness)
    """
    loop = asyncio.get_event_loop()
    sharpness1 = await loop.run_in_executor(None, compute_sharpness, img1_path)
    sharpness2 = await loop.run_in_executor(None, compute_sharpness, img2_path)
    if sharpness1 > sharpness2:
        return (img1_path, img2_path, sharpness1, sharpness2)
    else:
        return (
            img2_path,
            img1_path,
            sharpness2,
            sharpness1,
        )


async def async_analyze_pairs(img_pairs):
    results = []
    BATCH_SIZE = 5
    CHUNK_SIZE = len(img_pairs) // BATCH_SIZE

    with tqdm(total=len(img_pairs), desc="Processing pairs") as pbar:
        for chunk in chunkify(img_pairs, chunk_size=CHUNK_SIZE):
            tasks = [
                compare_pair(img1_path, img2_path) for img1_path, img2_path in chunk
            ]
            for future in asyncio.as_completed(tasks):
                result = await future
                results.append(result)
                pbar.update(1)  # Update the progress bar for each completed task
    return results
