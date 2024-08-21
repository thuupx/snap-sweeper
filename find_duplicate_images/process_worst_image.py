import os
from find_duplicate_images.utils import move_file

TO_BE_DELETED_DIR = "TO_BE_DELETED"


def process_worst_image(worst_img: str):
    BASE_DIR = worst_img.rsplit("/", 1)[0]
    if not BASE_DIR.endswith("/"):
        BASE_DIR += "/"

    BASE_DIR = os.path.join(BASE_DIR, TO_BE_DELETED_DIR)

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    move_file(worst_img, BASE_DIR)