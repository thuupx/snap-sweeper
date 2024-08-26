IMAGE_EMBEDDING_FILE = "imgs_embedding.pkl"

import torch

from find_duplicate_images.image_quality_comparator import ImageQualityComparator
from find_duplicate_images.process_images import (
    find_near_duplicates,
    get_image_pairs,
    load_embeddings,
)
from find_duplicate_images.process_worst_image import process_worst_image
from find_duplicate_images.utils import chunkify


async def find_and_move_duplicates_handler(
    img_folder, limit=0, batch_size=128, top_k=2, threshold=0.9, dry_run=False
) -> tuple[list[tuple[str, str, float, float, float]], str]:
    device = torch.device(
        "mps"
        if torch.backends.mps.is_built()
        else "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"Using device: {device}")
    print(f"Loading images from {img_folder}")
    print("Loading embeddings...")

    img_embedding, img_names_db = load_embeddings(
        img_folder, IMAGE_EMBEDDING_FILE, batch_size=batch_size, device=device
    )
    if img_embedding is None:
        print("No embeddings found or loaded.")
        return None, "No embeddings found or loaded."

    print("Finding near duplicates...")
    near_duplicates = find_near_duplicates(
        img_embedding, threshold=threshold, top_k=top_k
    )
    if limit > 0 and len(near_duplicates) > limit:
        near_duplicates = near_duplicates[:limit]

    if not near_duplicates:
        print("No near duplicates found.")
        return None, "No near duplicates found."

    img_pairs = get_image_pairs(near_duplicates, img_names_db)
    if not img_pairs:
        print("No valid near duplicates pairs found.")
        return None, "No valid near duplicates pairs found."

    print("Analyzing pairs...")
    image_quality_comparator = ImageQualityComparator()
    results = await image_quality_comparator.process_image_pairs(img_pairs)
    results = sorted(results, key=lambda x: x[4], reverse=True)

    print(f"Results: {len(results)}")
    results = list(chunkify(results, chunk_size=10))

    for chunk in results:
        for best_img, worst_img, best_score, worst_score, similarity in chunk:
            print(f"\n\nSimilarity Score: {similarity:.3f}")
            print(f"Best Quality Image: {best_img}, score: {best_score:.2f}")
            print(f"Worst Quality Image: {worst_img}, score: {worst_score:.2f}")
            if not dry_run:
                process_worst_image(worst_img)

    print("Completed!")
    return results, "Completed!"
