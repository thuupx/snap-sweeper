import cv2
import asyncio
from tqdm.asyncio import tqdm
from skimage.metrics import structural_similarity as ssim


from find_duplicate_images.utils import memorize_imread, chunkify


def compute_sharpness(image_path):
    """
    Computes the sharpness of an image using the Laplacian of Gaussian.
    """
    image = memorize_imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var


async def compare_pair(img1_path, img2_path):
    """
    Compares the sharpness, color, and layout of two images.

    @return: tuple of (best_img, worst_img, best_score, worst_score)
    """
    loop = asyncio.get_event_loop()

    # Run tasks concurrently
    sharpness1_task = loop.run_in_executor(None, compute_sharpness, img1_path)
    sharpness2_task = loop.run_in_executor(None, compute_sharpness, img2_path)
    color_similarity_task = loop.run_in_executor(
        None, compute_color_similarity, img1_path, img2_path
    )
    layout_similarity_task = loop.run_in_executor(
        None, compute_layout_similarity, img1_path, img2_path
    )

    # Await the results
    sharpness1, sharpness2, color_similarity, layout_similarity = await asyncio.gather(
        sharpness1_task, sharpness2_task, color_similarity_task, layout_similarity_task
    )

    score1 = sharpness1 + color_similarity + layout_similarity
    score2 = sharpness2 + color_similarity + layout_similarity

    if score1 > score2:
        return (img1_path, img2_path, score1, score2)
    else:
        return (img2_path, img1_path, score2, score1)


def compute_color_similarity(image_path1, image_path2):
    """
    Computes the color similarity between two images using histogram comparison.
    """
    image1 = memorize_imread(image_path1)
    image2 = memorize_imread(image_path2)

    if image1 is None or image2 is None:
        return 0

    hsv_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
    hsv_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)

    hist_image1 = cv2.calcHist([hsv_image1], [0, 1], None, [50, 60], [0, 180, 0, 256])
    hist_image2 = cv2.calcHist([hsv_image2], [0, 1], None, [50, 60], [0, 180, 0, 256])

    cv2.normalize(hist_image1, hist_image1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist_image2, hist_image2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    color_similarity = cv2.compareHist(hist_image1, hist_image2, cv2.HISTCMP_INTERSECT)

    return color_similarity


def compute_layout_similarity(image_path1, image_path2):
    """
    Computes the layout similarity between two images using SSIM.
    """
    image1 = memorize_imread(image_path1, cv2.IMREAD_GRAYSCALE)
    image2 = memorize_imread(image_path2, cv2.IMREAD_GRAYSCALE)

    if image1 is None or image2 is None:
        return 0

    ssim_index, _ = ssim(image1, image2, full=True)

    return ssim_index


async def analyze_pairs(img_pairs):
    results = []
    BATCH_SIZE = 5
    CHUNK_SIZE = len(img_pairs) // BATCH_SIZE

    with tqdm(total=len(img_pairs), desc="Processing pairs") as progress_bar:
        for chunk in chunkify(img_pairs, chunk_size=CHUNK_SIZE):
            tasks = [
                compare_pair(img1_path, img2_path) for img1_path, img2_path in chunk
            ]
            for future in asyncio.as_completed(tasks):
                result = await future
                results.append(result)
                progress_bar.update(1)
    return results
