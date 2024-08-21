import os
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer, util

DEFAULT_MODEL = SentenceTransformer("clip-ViT-B-32")


def load_image(filepath):
    return Image.open(filepath)


def encode_images(image_paths, model, batch_size=128, device=None):
    """
    Encodes a list of images using the given model.
    """
    all_embeddings = []

    # Use ThreadPoolExecutor for concurrent image loading
    with ThreadPoolExecutor() as executor:
        for start_idx in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[start_idx : start_idx + batch_size]
            images = list(executor.map(load_image, batch_paths))
            embeddings = model.encode(
                images,
                batch_size=batch_size,
                convert_to_tensor=True,
                show_progress_bar=True,
                device=device,
            )
            all_embeddings.append(embeddings)
    return torch.cat(all_embeddings, dim=0)


def load_embeddings(img_folder, embedding_file, batch_size=128, device=None):
    """
    Loads the embeddings from the given file or computes them if they don't exist.
    """
    from find_duplicate_images.utils import get_image_files

    img_names = get_image_files(img_folder)

    img_embedding: np.ndarray | None = None
    existing_img_names: list[str] = []

    # load embedding
    if os.path.exists(embedding_file) and os.path.getsize(embedding_file) > 0:
        with open(embedding_file, "rb") as f:
            existing_data = np.load(f, allow_pickle=True).item()
            img_embedding = existing_data["embeddings"]
            existing_img_names = existing_data["img_names"]
            print("Embedding loaded shape: ", img_embedding.shape)
    else:
        print(f"File {embedding_file} not found, loading images...")

    # Only load images that are not in the existing embeddings
    new_img_names = [
        img_name for img_name in img_names if img_name not in existing_img_names
    ]
    print("New images to load:", len(new_img_names))

    if len(new_img_names) == 0:
        return img_embedding, existing_img_names
    else:
        start_time = time.time()
        new_img_embeddings = encode_images(
            new_img_names, DEFAULT_MODEL, batch_size, device
        )
        print(f"Encoding images took {(time.time() - start_time):.2f} seconds")

        # Convert new embeddings to CPU and combine with existing embeddings
        if img_embedding is not None:
            img_embedding = np.concatenate(
                (img_embedding, new_img_embeddings.cpu().numpy()), axis=0
            )
            img_names = existing_img_names + new_img_names
        else:
            img_embedding = new_img_embeddings.cpu().numpy()
            img_names = new_img_names

        # Save the combined embeddings and image names
        with open(embedding_file, "wb") as f:
            np.save(
                f,
                {"embeddings": img_embedding, "img_names": img_names},
                allow_pickle=True,
            )

    return img_embedding, img_names


def find_near_duplicates(img_embedding: np.ndarray, threshold=0.9, top_k=10):
    MAX_THRESHOLD = 1
    duplicates = util.paraphrase_mining_embeddings(img_embedding, top_k=top_k)
    near_duplicates = [
        entry
        for entry in duplicates
        if entry[0] <= MAX_THRESHOLD and entry[0] > threshold
    ]

    return near_duplicates


def get_image_pairs(near_duplicates: list[list[float | int]], all_img_names: list[str]):
    """Get image pairs from the near duplicates list."""
    # Collect a set of all image names that need to be checked
    required_files = {
        all_img_names[embedding_idx1]
        for _, embedding_idx1, embedding_idx2 in near_duplicates
    }.union(
        {
            all_img_names[embedding_idx2]
            for _, embedding_idx1, embedding_idx2 in near_duplicates
        }
    )

    # Use set comprehensions for quick lookup
    existing_files = {
        img_name for img_name in required_files if os.path.exists(img_name)
    }

    return [
        (all_img_names[embedding_idx1], all_img_names[embedding_idx2], similarity)
        for (similarity, embedding_idx1, embedding_idx2) in near_duplicates
        if all_img_names[embedding_idx1] in existing_files
        and all_img_names[embedding_idx2] in existing_files
    ]
