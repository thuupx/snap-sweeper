import argparse
import asyncio
import time

from .utils import chunkify

IMAGE_EMBEDDING_FILE = "imgs_embedding.pkl"


async def main(args):
    start_time = time.time()
    img_folder = args.dir
    limit = args.limit
    batch_size = args.batch_size
    top_k = args.top_k
    import torch

    from find_duplicate_images.compare_image_quality import analyze_pairs

    device = torch.device(
        "mps"
        if torch.backends.mps.is_built()
        else "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"Using device: {device}")
    print(f"Loading images from {img_folder}")
    print("Loading embeddings...")
    from find_duplicate_images.process_images import load_embeddings

    img_embedding, img_names_db = load_embeddings(
        img_folder, IMAGE_EMBEDDING_FILE, batch_size=batch_size, device=device
    )
    if img_embedding is None:
        print("No embeddings found or loaded.")
        return

    print("Finding near duplicates...")
    from find_duplicate_images.process_images import find_near_duplicates

    near_duplicates = find_near_duplicates(img_embedding, threshold=1, top_k=top_k)
    if limit > 0 and len(near_duplicates) > limit:
        near_duplicates = near_duplicates[:limit]

    if len(near_duplicates) == 0:
        print("No near duplicates found.")
        return

    from find_duplicate_images.process_images import get_image_pairs

    img_pairs = get_image_pairs(near_duplicates, img_names_db)

    if len(img_pairs) == 0:
        print("No valid near duplicates pairs found.")
        return

    print("Analyzing pairs...")
    results = await analyze_pairs(
        img_pairs,
    )

    results = sorted(results, key=lambda x: x[4], reverse=True)

    print("Results: ", len(results))
    # Chunk the results into smaller chunks for better performance
    results = list(chunkify(results, chunk_size=10))
    from find_duplicate_images.process_worst_image import process_worst_image

    for chunk in results:
        for i, (best_img, worst_img, best_score, worst_score, similarity) in enumerate(
            chunk
        ):
            print("\n\nSimilarity Score: {:.3f}".format(similarity))
            print(f"Best Quality Image: {best_img}, score: {best_score:.2f}")
            print(f"Worst Quality Image: {worst_img}, score: {worst_score:.2f}")
            process_worst_image(worst_img)

    print(f"Total time: {(time.time() - start_time):.2f} seconds")
    print("Done.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find and compare duplicate images based on sharpness, color, and layout."
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        required=True,
        help="Directory containing the images to process.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit the number of near duplicates to process. Default is no limit.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="Batch size to use when encoding images. Default is 128.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of near duplicates to find. Default is 10.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
