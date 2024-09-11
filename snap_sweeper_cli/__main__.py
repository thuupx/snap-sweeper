import sys
from core.error_handling import global_exception_handler
from core.find_and_move_similar_images import (
    find_and_move_similar_images,
)

sys.excepthook = global_exception_handler


async def main(args):
    import time

    start_time = time.time()
    img_folder = args.dir
    limit = args.limit
    top_k = args.top_k
    threshold = args.threshold
    dry_run = args.dry_run

    if dry_run:
        print("Dry run mode enabled. No images will be moved.")

    await find_and_move_similar_images(
        img_folder,
        limit=limit,
        top_k=top_k,
        threshold=threshold,
        dry_run=dry_run,
    )
    print(f"Total time: {(time.time() - start_time):.2f} seconds")


def parse_args():
    import argparse

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
        default=None,
        help="Limit the number of near duplicates to process. Default is no limit.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=2,
        help="Number of near duplicates to find. Default is 2.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.9,
        help="Threshold for similarity score. Default is 0.9.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode. Only prints the results without moving the images.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    import asyncio

    asyncio.run(main(args))
