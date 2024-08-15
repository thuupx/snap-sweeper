from find_duplicate_images.utils import copy_file

WORST_IMAGE_DIR = "worst_images"


def process_worst_image(worst_img: str):
    copy_file(worst_img, WORST_IMAGE_DIR)
