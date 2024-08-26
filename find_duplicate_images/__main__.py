async def main(args):
    import time

    start_time = time.time()
    img_folder = args.dir
    limit = args.limit
    batch_size = args.batch_size
    top_k = args.top_k
    threshold = args.threshold
    dry_run = args.dry_run
    from find_duplicate_images.handler import find_and_move_duplicates_handler

    await find_and_move_duplicates_handler(
        img_folder,
        limit=limit,
        batch_size=batch_size,
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
