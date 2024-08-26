IMAGE_EMBEDDING_FILE = "imgs_embedding.pkl"


from find_duplicate_images.image_processor import ImageProcessor
from find_duplicate_images.image_quality_comparator import ImageQualityComparator
from find_duplicate_images.utils import chunkify, move_files_to_subdir


async def find_and_move_duplicates_handler(
    img_folder, limit=0, batch_size=128, top_k=2, threshold=0.9, dry_run=False
) -> tuple[list[tuple[str, str, float, float, float]], str]:

    print(f"Loading images from {img_folder}")

    image_processor = ImageProcessor(embedding_file=IMAGE_EMBEDDING_FILE)
    image_quality_comparator = ImageQualityComparator()

    print("Loading embeddings...")
    img_embedding, img_names_db = image_processor.load_embeddings(
        img_folder, batch_size=batch_size
    )
    if img_embedding is None:
        print("No embeddings found or loaded.")
        return None, "No embeddings found or loaded."

    print("Finding near duplicates...")
    near_duplicates = image_processor.search(
        img_embedding, threshold=threshold, top_k=top_k, limit=limit
    )

    if not near_duplicates:
        print("No near duplicates found.")
        return None, "No near duplicates found."

    img_pairs = image_processor.generate_image_pairs(near_duplicates, img_names_db)
    if not img_pairs:
        print("No valid near duplicates pairs found.")
        return None, "No valid near duplicates pairs found."

    print("Analyzing pairs...")
    results = await image_quality_comparator.process_image_pairs(img_pairs)
    results = sorted(results, key=lambda x: x[4], reverse=True)

    print(f"Results: {len(results)}")

    discarded_images = set(map(lambda x: x[1], results))

    if dry_run:
        results = list(chunkify(results, chunk_size=10))
        for chunk in results:
            for best_img, worst_img, best_score, worst_score, similarity in chunk:
                print(f"\n\nSimilarity Score: {similarity:.3f}")
                print(f"Best Quality Image: {best_img}, score: {best_score:.2f}")
                print(f"Worst Quality Image: {worst_img}, score: {worst_score:.2f}")
    else:
        print(f"Discarded images: {len(discarded_images)}")
        DISCARDED_DIR = "DISCARDED"
        await move_files_to_subdir(discarded_images, DISCARDED_DIR)

    print("Completed!")
    return results, "Completed!"
