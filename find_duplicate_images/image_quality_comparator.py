import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import cv2
from brisque import BRISQUE as Btisque
from numpy import asarray
from tqdm.asyncio import tqdm

from find_duplicate_images.utils import chunkify, memorize_imread


class ImageQualityComparator:
    def __init__(self):
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=1)

    def get_np_array(self, img_path, pixel_x=64, pixel_y=64):
        img = memorize_imread(img_path)
        cvt = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(cvt, (pixel_x, pixel_y))
        ndarray = asarray(resized)
        return ndarray

    def compute_quality_score(self, img_path: str) -> float:
        np_array = self.get_np_array(img_path)
        with self.lock:
            score = self.executor.submit(Btisque(url=False).score, img=np_array)
            score = score.result()
            return score

    async def compare_image_quality(
        self, img1_path: str, img2_path: str, similarity: float
    ):
        """
        Compares scores of two images.

        Return tuple of (best_image_path, worst_image_path, best_score, worst_score, similarity)
        """
        loop = asyncio.get_event_loop()
        score1_task = loop.run_in_executor(None, self.compute_quality_score, img1_path)
        score2_task = loop.run_in_executor(None, self.compute_quality_score, img2_path)

        q_score1, q_score2 = await asyncio.gather(score1_task, score2_task)

        if q_score1 > q_score2:
            return (img1_path, img2_path, q_score1, q_score2, similarity)
        else:
            return (img2_path, img1_path, q_score2, q_score1, similarity)

    async def process_image_pairs(
        self, img_pairs: list[tuple[str, str, float]]
    ) -> list[tuple[str, str, float, float, float]]:
        results = []
        BATCH_SIZE = 5
        CHUNK_SIZE = len(img_pairs) // BATCH_SIZE

        with tqdm(total=len(img_pairs), desc="Processing pairs") as progress_bar:
            for chunk in chunkify(img_pairs, chunk_size=CHUNK_SIZE):
                tasks = [
                    self.compare_image_quality(img1_path, img2_path, similarity)
                    for img1_path, img2_path, similarity in chunk
                ]
                for future in asyncio.as_completed(tasks):
                    result = await future
                    results.append(result)
                    progress_bar.update(1)
        return results
