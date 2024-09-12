import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from brisque import BRISQUE as Btisque
from numpy import asarray
from PIL import Image
from tqdm.asyncio import tqdm

from .utils import chunkify


class ImageQualityComparator:
    def __init__(self, max_concurrency: int | None = None):
        self.lock = Lock()
        max_concurrency = max_concurrency or (os.cpu_count() or 4) * 2
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.scoring_executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
        self.quality_executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)

    def get_numpy_array(self, img_path, pixel_x=64, pixel_y=64):
        img = Image.open(img_path)
        resized = img.resize((pixel_x, pixel_y))
        ndarray = asarray(resized)
        return ndarray

    def compute_quality_score(self, img_path: str) -> float:
        np_array = self.get_numpy_array(img_path)
        with self.lock:
            score = self.scoring_executor.submit(Btisque(url=False).score, img=np_array)
            score = score.result()
            return score

    async def compare_image_quality(
        self, similarity: float, img1_path: str, img2_path: str
    ):
        """
        Compares the quality of two images and returns a tuple containing the best and worst image paths, their scores, and the similarity score.

        Parameters:
            similarity (float): The similarity score between the two images.
            img1_path (str): The path to the first image.
            img2_path (str): The path to the second image.

        Returns:
            tuple: A tuple containing the best and worst image paths, their scores, and the similarity score.
        """
        loop = asyncio.get_event_loop()

        score1_task = loop.run_in_executor(
            self.quality_executor, self.compute_quality_score, img1_path
        )
        score2_task = loop.run_in_executor(
            self.quality_executor, self.compute_quality_score, img2_path
        )

        q_score1, q_score2 = await asyncio.gather(score1_task, score2_task)

        if q_score1 > q_score2:
            return (img1_path, img2_path, q_score1, q_score2, similarity)
        else:
            return (img2_path, img1_path, q_score2, q_score1, similarity)

    async def perform_image_quality_comparison(
        self, img_pairs: list[tuple[float, str, str]]
    ) -> list[tuple[str, str, float, float, float]]:
        """
        Compares the quality of a list of image pairs and returns a list of tuples containing the best and worst image paths, their scores, and the similarity score.

        Parameters:
            img_pairs (list[tuple[float, str, str]]): A list of tuples containing the similarity score, the paths of the two images.

        Returns:
            list[tuple[str, str, float, float, float]]: A list of tuples containing the best and worst image paths, their scores, and the similarity score.
        """
        results = []
        CHUNK_SIZE = 10

        with tqdm(total=len(img_pairs), desc="Processing pairs") as progress_bar:
            for chunk in chunkify(img_pairs, chunk_size=CHUNK_SIZE):
                tasks = [
                    asyncio.create_task(
                        self._limited_compare_image_quality(
                            similarity, img1_path, img2_path
                        )
                    )
                    for similarity, img1_path, img2_path in chunk
                ]
                for future in asyncio.as_completed(tasks):
                    result = await future
                    results.append(result)
                    progress_bar.update(1)
        return results

    async def _limited_compare_image_quality(
        self, similarity: float, img1_path: str, img2_path: str
    ):
        async with self.semaphore:
            return await self.compare_image_quality(similarity, img1_path, img2_path)
