import asyncio
import queue
import sys
import time
from typing import Any, List
from pathlib import Path

import chromadb
from chromadb.api.types import IncludeEnum
from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import (
    SentenceTransformerEmbeddingFunction,
)
from PIL import Image
from sentence_transformers import util
from tqdm.asyncio import tqdm

from .utils import chunkify

MODEL_NAME = "clip-ViT-B-32"
DB_PATH_NAME = "database"


class ImageAnalyzer:
    def __init__(self):
        self._setup_database()

    def _setup_database(self):
        self.client = chromadb.PersistentClient(path=self._get_database_path())
        embedding_function: Any = SentenceTransformerEmbeddingFunction(
            model_name=MODEL_NAME, device=util.get_device_name()
        )
        self.collection = self.client.get_or_create_collection(
            name="image_embeddings",
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_function,
        )

    @staticmethod
    async def _load_image(filepath: str):
        image = Image.open(filepath)
        return image

    @staticmethod
    async def _async_load_images(batch_paths: list[str]):
        images = await asyncio.gather(
            *[ImageAnalyzer._load_image(path) for path in batch_paths]
        )
        return images

    @staticmethod
    def _get_database_path():
        if getattr(sys, "frozen", False):
            # Running as compiled application
            app_path = Path(sys.executable).parent.parent
            db_path = app_path / "Contents" / "Resources" / DB_PATH_NAME
        else:
            # Running in a normal Python environment
            db_path = Path("./" + DB_PATH_NAME)

        # Use Application Support directory on macOS
        if sys.platform == "darwin":
            db_path = (
                Path.home()
                / "Library"
                / "Application Support"
                / "SnapSweep"
                / DB_PATH_NAME
            )

        # Ensure the directory exists
        db_path.mkdir(parents=True, exist_ok=True)
        return str(db_path)

    async def add_images(self, image_paths: list[str]):
        """
        Adds the given image paths to the database.

        Parameters:
            image_paths (list[str]): A list of image paths to add to the database.
        """
        images: List[Any] = await ImageAnalyzer._async_load_images(image_paths)
        self.collection.add(
            ids=image_paths,
            images=images,
            metadatas=[{"path": path} for path in image_paths],
        )

    async def create_embeddings_if_not_exist(self, image_paths: list[str]):
        """
        Creates embeddings for the given image paths if they don't already exist in the database.
        """
        current_image_paths = self.collection.get(ids=image_paths)["ids"]
        image_paths = [path for path in image_paths if path not in current_image_paths]
        if len(image_paths) > 0:
            print(f"Creating embeddings for {len(image_paths)} images...")
            start_time = time.time()
            with tqdm(
                total=len(image_paths), desc="Creating embeddings"
            ) as progress_bar:
                CHUNK_SIZE = len(image_paths) % 10
                print(f"Chunk size: {CHUNK_SIZE}")
                for chunk in chunkify(image_paths, chunk_size=CHUNK_SIZE):
                    tasks = [self.add_images(chunk)]
                    await asyncio.gather(*tasks)
                    progress_bar.update(len(chunk))
            print("Embeddings created in %.2f seconds" % (time.time() - start_time))
        else:
            print("All images are already embedded.")

    @staticmethod
    def paraphrase_mining_embeddings(
        embeddings: List[chromadb.Embeddings],
        metadatas: List[chromadb.Metadata],
        top_k=100,
        max_pairs=500000,
        query_chunk_size=5000,
        corpus_chunk_size=100000,
    ) -> List[tuple[float, str, str]]:
        """
        Finds near-duplicate images based on embeddings stored in the database.

        Args:
            embeddings: torch.Tensor
                The embeddings to search for near-duplicates.
            top_k: int
                The number of near-duplicates to find.
            max_pairs: int
                The maximum number of near-duplicates to find.
            query_chunk_size: int
                The size of the query chunk.
            corpus_chunk_size: int
                The size of the corpus chunk.
            metadatas: chromadb.Metadata
                The metadatas to use for the search.
        Returns:
            list of tuple: A list containing tuples of similarity score and the paths of the near-duplicate images.
        """

        top_k += 1
        pairs = queue.PriorityQueue()
        min_score = -1
        num_added = 0
        import torch

        for corpus_start_idx in range(0, len(embeddings), corpus_chunk_size):
            for query_start_idx in range(0, len(embeddings), query_chunk_size):
                scores = util.cos_sim(
                    embeddings[query_start_idx : query_start_idx + query_chunk_size],
                    embeddings[corpus_start_idx : corpus_start_idx + corpus_chunk_size],
                )

                scores_top_k_values, scores_top_k_idx = torch.topk(
                    scores,
                    min(top_k, len(scores[0])),
                    dim=1,
                    largest=True,
                    sorted=False,
                )
                scores_top_k_values = scores_top_k_values.cpu().tolist()
                scores_top_k_idx = scores_top_k_idx.cpu().tolist()

                for query_itr in range(len(scores)):
                    for top_k_idx, corpus_itr in enumerate(scores_top_k_idx[query_itr]):
                        i = query_start_idx + query_itr
                        j = corpus_start_idx + corpus_itr

                        if (
                            i != j
                            and scores_top_k_values[query_itr][top_k_idx] > min_score
                        ):
                            pairs.put((scores_top_k_values[query_itr][top_k_idx], i, j))
                            num_added += 1

                            if num_added >= max_pairs:
                                entry = pairs.get()
                                min_score = entry[0]

        # Get the pairs
        added_pairs = set()  # Used for duplicate detection
        pairs_list: List[tuple[float, str, str]] = []
        while not pairs.empty():
            score, i, j = pairs.get()
            sorted_i, sorted_j = sorted([i, j])

            if sorted_i != sorted_j and (sorted_i, sorted_j) not in added_pairs:
                added_pairs.add((sorted_i, sorted_j))
                pairs_list.append(
                    (score, metadatas[sorted_i]["path"], metadatas[sorted_j]["path"])
                )

        # Highest scores first
        pairs_list = sorted(pairs_list, key=lambda x: x[0], reverse=True)
        return pairs_list

    def similarity_search(
        self, image_paths: list[str], top_k=10, limit: int | None = None, threshold=0.9
    ) -> List[tuple[float, str, str]]:
        """
        Search for near duplicates using the given image embeddings.

        Parameters:
            image_paths (list[str]): A list of image paths to search for near duplicates.
            top_k (int): The number of near duplicates to find.
            limit (int): The maximum number of near duplicates to find.

        Returns:
            list: A list of tuples containing the similarity score, the paths of the two images.
        """
        all_docs = self.collection.get(
            ids=image_paths,
            limit=limit,
            include=[IncludeEnum.embeddings, IncludeEnum.metadatas],
        )
        embeddings: List[Any] = all_docs["embeddings"] or []
        metadatas: List[Any] = all_docs["metadatas"] or []

        duplicates = ImageAnalyzer.paraphrase_mining_embeddings(
            embeddings=embeddings, top_k=top_k, metadatas=metadatas
        )
        near_duplicates = [
            entry for entry in duplicates if round(float(entry[0]), 2) >= threshold
        ]

        if limit is not None:
            near_duplicates = near_duplicates[:limit]

        return near_duplicates

    @staticmethod
    def remove_invalid_pairs(near_duplicates: list[tuple[float, str, str]]):
        """
        Generate image pairs from the near duplicates list.

        Ignores images that are not in the image folder.

        Parameters:
            near_duplicates (list): A list of tuples containing the similarity score, the paths of the two images.

        Returns:
            list: A list of tuples containing the image names, the indices of the two images, and the similarity score.
        """
        import os

        valid_pairs = [
            (score, img1_path, img2_path)
            for score, img1_path, img2_path in near_duplicates
            if os.path.exists(img1_path) and os.path.exists(img2_path)
        ]

        return valid_pairs
