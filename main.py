from sentence_transformers import SentenceTransformer, util
from PIL import Image
import glob
import os
import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor
import time
import asyncio


from async_compare_image_quality import async_analyze_pairs
from utils import chunkify

IMAGE_EMBEDDING_FILE = "imgs_embedding.pkl"
model = SentenceTransformer("clip-ViT-B-32")


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
                show_progress_bar=False,
                device=device,
            )
            all_embeddings.append(embeddings)
    return torch.cat(all_embeddings, dim=0)


def load_embeddings(img_folder, embedding_file, batch_size=128, device=None):
    """
    Loads the embeddings from the given file or computes them if they don't exist.
    """
    img_names = list(glob.glob(os.path.join(img_folder, "*.JPG")))

    img_embedding = None
    existing_img_names = []

    # load embedding
    if os.path.exists(embedding_file) and os.path.getsize(embedding_file) > 0:
        with open(embedding_file, "rb") as f:
            existing_data = np.load(f, allow_pickle=True).item()
            img_embedding = existing_data["embeddings"]
            existing_img_names = existing_data["img_names"]
            print("Embedding loaded:", img_embedding.shape[0])
    else:
        print(f"File {embedding_file} not found, loading images...")

    # Only load images that are not in the existing embeddings
    new_img_names = [
        img_name for img_name in img_names if img_name not in existing_img_names
    ]
    print("New images to load:", len(new_img_names))

    if new_img_names:
        start_time = time.time()
        new_img_embeddings = encode_images(new_img_names, model, batch_size, device)
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


def find_near_duplicates(img_embedding, threshold=1, top_k=10):
    duplicates = util.paraphrase_mining_embeddings(img_embedding, top_k=top_k)
    print(f"Found {len(duplicates)} duplicates")
    near_duplicates = [entry for entry in duplicates if entry[0] <= threshold]
    return near_duplicates


def get_image_pairs(near_duplicates, img_names):
    return [(img_names[idx1], img_names[idx2]) for (_, idx1, idx2) in near_duplicates]


async def main():
    img_folder = "/Users/thupx/Documents/ThuPX/img"
    device = torch.device("mps" if torch.backends.mps.is_built() else "cpu")
    print(f"Using device: {device}")
    print(f"Loading images from {img_folder}")
    print("Loading embeddings...")
    img_embedding, img_names = load_embeddings(
        img_folder, IMAGE_EMBEDDING_FILE, batch_size=128, device=device
    )
    if img_embedding is None:
        print("No embeddings found or loaded.")
        return

    print(img_embedding.shape)

    print("Finding near duplicates...")
    near_duplicates = find_near_duplicates(img_embedding, threshold=1, top_k=10)[:10]
    img_pairs = get_image_pairs(near_duplicates, img_names)

    print("Analyzing pairs...")
    results = await async_analyze_pairs(
        img_pairs,
    )

    # Chunk the results into smaller chunks for better performance
    results = list(chunkify(results, chunk_size=10))

    for chunk in results:
        for i, (best_img, worst_img, best_sharpness, worst_sharpness) in enumerate(
            chunk
        ):
            score, idx1, idx2 = near_duplicates[i]
            print("\n\nScore: {:.3f}".format(score))
            print(f"Best Quality Image: {best_img}, Sharpness: {best_sharpness:.2f}")
            print(f"Worst Quality Image: {worst_img}, Sharpness: {worst_sharpness:.2f}")

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
