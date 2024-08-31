from find_duplicate_images.core.image_analyzer import ImageAnalyzer
from find_duplicate_images.core.image_quality_comparator import ImageQualityComparator
from find_duplicate_images.core.utils import (
    chunkify,
    get_image_files,
    move_files_to_subdir,
)


async def find_and_move_similar_images(
    img_folder: str, limit: int = None, top_k=2, threshold=0.9, dry_run=False
):
    """
    Find and move similar images based on their similarity.

    Parameters:
        img_folder (str): The folder containing the images to process.
        limit (int): The maximum number of near duplicates to find. Default is None.
        batch_size (int): The batch size to use for encoding images. Default is 32.
        top_k (int): The number of near duplicates to find. Default is 2.
        threshold (float): The similarity threshold for considering two images as near duplicates. Default is 0.9.
        dry_run (bool): Whether to run the process in dry run mode. Default is False.

    Returns:
        tuple: A tuple containing a list of tuples containing the best and worst image paths, their scores, and the similarity score, and a string containing the error message if any.
    """

    image_analyzer = ImageAnalyzer()
    image_quality_comparator = ImageQualityComparator()

    image_files = await get_image_files(img_folder)
    await image_analyzer.create_embeddings_if_not_exist(image_files)

    search_results = image_analyzer.similarity_search(
        image_files, top_k=top_k, limit=limit, threshold=threshold
    )

    if not search_results:
        print("No near duplicates found.")
        return None, "No near duplicates found."

    valid_pairs = ImageAnalyzer.remove_invalid_pairs(search_results)

    if not valid_pairs:
        print("No valid near duplicates pairs found.")
        return None, "No valid near duplicates pairs found."

    print("Analyzing pairs...")
    results = await image_quality_comparator.perform_image_quality_comparison(
        valid_pairs
    )
    results = sorted(results, key=lambda x: x[4], reverse=True)
    returned_results = results

    print(f"Results: {len(results)}")
    discarded_images = set(map(lambda x: x[1], results))
    print(f"Discarded images: {len(discarded_images)}")
    if dry_run:
        results = list(chunkify(results, chunk_size=10))
        for chunk in results:
            for best_img, worst_img, best_score, worst_score, similarity in chunk:
                print(f"\n\nSimilarity Score: {similarity:.3f}")
                print(f"Best Quality Image: {best_img}, score: {best_score:.2f}")
                print(f"Worst Quality Image: {worst_img}, score: {worst_score:.2f}")
    else:
        DISCARDED_DIR = "DISCARDED"
        await move_files_to_subdir(discarded_images, DISCARDED_DIR)

    print("Completed!")
    return returned_results, None
