DISCARDED_DIR = "DISCARDED"


def process_worst_image(worst_img: str):
    import os
    from find_duplicate_images.utils import move_file

    BASE_DIR = worst_img.rsplit("/", 1)[0]
    if not BASE_DIR.endswith("/"):
        BASE_DIR += "/"

    BASE_DIR = os.path.join(BASE_DIR, DISCARDED_DIR)

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    move_file(worst_img, BASE_DIR)
