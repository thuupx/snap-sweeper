import time

from .image_analyzer import ImageAnalyzer
from .image_quality_comparator import ImageQualityComparator
from .utils import calculate_file_hashes, get_image_files, move_files_to_subdir


async def find_and_move_similar_images(
    img_folder: str,
    limit: int | None = None,
    top_k=2,
    threshold=0.9,
    dry_run=False,
    sub_folder_name="DISCARDED",
    include_subdirs=True,
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
    start_time = time.time()
    image_analyzer = ImageAnalyzer()
    image_quality_comparator = ImageQualityComparator()

    image_files = await get_image_files(img_folder, include_subdirs)
    print(f"Found {len(image_files)} image files")
    if len(image_files) == 0:
        print("No image files found.")
        return None, None, "No image files found."
    path_to_hash_map = await calculate_file_hashes(image_files)
    await image_analyzer.update_image_index(path_to_hash_map)
    search_results = await image_analyzer.similarity_search(
        path_to_hash_map=path_to_hash_map,
        top_k=top_k,
        limit=limit,
        threshold=threshold,
    )

    if not search_results:
        print("No near duplicates found.")
        return None, None, "No near duplicates found."

    valid_pairs = image_analyzer.remove_invalid_pairs(search_results)

    if not valid_pairs:
        print("No valid near duplicates pairs found.")
        return None, None, "No valid near duplicates pairs found."

    print("Image quality comparison is processing...")
    results = await image_quality_comparator.perform_image_quality_comparison(
        valid_pairs
    )
    results = sorted(results, key=lambda x: x[4], reverse=True)
    returned_results = results

    print(f"Total valid similarity pairs: {len(results)}")
    discarded_images = set(map(lambda x: x[1], results))
    print(
        f"Total similarity low quality images (to be deleted): {len(discarded_images)}"
    )
    if dry_run:
        print("Dry run mode enabled, skipping image deletion.")
    else:
        await move_files_to_subdir(list(discarded_images), sub_folder_name)

    print("Completed in %.2f seconds" % (time.time() - start_time))
    return returned_results, discarded_images, None
