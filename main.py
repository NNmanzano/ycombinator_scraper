"""
Entry point. Run with:

    venv\\Scripts\\python main.py --batches "Winter 2025" --limit 10

See README.md for full usage and the directory layout.
"""
import argparse
import asyncio

import nodriver as uc

from src import config
from src.pipeline import YCombinatorPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YCombinator companies + founders scraper")
    parser.add_argument(
        "--batches",
        nargs="+",
        default=config.DEFAULT_BATCHES,
        help='YC batch names, e.g. --batches "Winter 2025" "Summer 2025"',
    )
    parser.add_argument("--limit", type=int, default=None, help="Only scrape the first N companies")
    parser.add_argument("--show-browser", action="store_true", help="Run Chrome non-headless (debugging)")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    pipeline = YCombinatorPipeline(
        batches=args.batches,
        headless=not args.show_browser,
        limit=args.limit,
    )
    await pipeline.run()


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
