import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import cv2
import numpy as np
from brisque import BRISQUE
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from tqdm.asyncio import tqdm

from find_duplicate_images.utils import chunkify, memorize_imread

lock = Lock()


def compute_sharpness(image_path):
    """
    Computes the sharpness of an image using the Laplacian of Gaussian.
    """
    image = memorize_imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var


def get_np_array(img_path):
    img = memorize_imread(img_path)
    cvt = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(cvt, (64, 64))
    ndarray = np.asarray(resized)
    return ndarray


def compute_brisque_score(img_path):
    np_array = get_np_array(img_path)
    with ThreadPoolExecutor(max_workers=1) as executor:
        with lock:
            score = executor.submit(BRISQUE(url=False).score, img=np_array)
            score = score.result()
            return score


async def image_quality_analysis(img1_path, img2_path, similarity):
    """
    Compares scores of two images.
    """
    loop = asyncio.get_event_loop()

    score1_task = loop.run_in_executor(None, compute_brisque_score, img1_path)
    score2_task = loop.run_in_executor(None, compute_brisque_score, img2_path)

    q_score1, q_score2 = await asyncio.gather(score1_task, score2_task)

    if q_score1 > q_score2:
        return (img1_path, img2_path, q_score1, q_score2, similarity)
    else:
        return (img2_path, img1_path, q_score2, q_score1, similarity)


async def analyze_pairs(img_pairs):
    results = []
    BATCH_SIZE = 5
    CHUNK_SIZE = len(img_pairs) // BATCH_SIZE

    with tqdm(total=len(img_pairs), desc="Processing pairs") as progress_bar:
        for chunk in chunkify(img_pairs, chunk_size=CHUNK_SIZE):
            tasks = [
                image_quality_analysis(img1_path, img2_path, similarity)
                for img1_path, img2_path, similarity in chunk
            ]
            for future in asyncio.as_completed(tasks):
                result = await future
                results.append(result)
                progress_bar.update(1)
    return results
