from core.find_and_move_similar_images import (
    find_and_move_similar_images,
)
from core.utils import move_files_to_subdir


class SnapSweeper:
    def __init__(self):
        self.discarded_images: list[str] = []

    async def process_images(self, image_dir, settings):
        return await find_and_move_similar_images(
            image_dir,
            dry_run=bool(settings["dry_run"]),
            top_k=int(settings["top_k"]),
            threshold=float(settings["threshold"]),
            sub_folder_name=str(settings["sub_folder_name"]),
        )

    async def move_discarded_images(self, sub_folder_name):
        discarded_images = list(self.discarded_images)
        print(f"Moving {len(discarded_images)} images to {sub_folder_name}")
        await move_files_to_subdir(discarded_images, sub_folder_name)
        print("Completed")
        print(
            f"Now you can review the images again in {sub_folder_name} and delete them manually."
        )
