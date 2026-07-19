"""CLI entry point for Disney+ catalog scraper (via JustWatch)."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from scraper.config import CATALOG_JSONL, CHECKPOINT_FILE, SEED_DIR, Settings, ensure_raw_dir
from scraper.justwatch_client import JustWatchClient, iter_catalog
from scraper.justwatch_normalize import normalize_justwatch_node

logger = logging.getLogger(__name__)

SAMPLE_CATALOG = SEED_DIR / "sample_catalog.jsonl"


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
    return {"scraped_ids": [], "cursor": None}


def save_checkpoint(checkpoint: dict) -> None:
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")


def write_jsonl(records: list[dict], path: Path = CATALOG_JSONL) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, default=str) + "\n")


def append_jsonl(records: list[dict], path: Path = CATALOG_JSONL) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, default=str) + "\n")


def use_sample_catalog() -> int:
    ensure_raw_dir()
    if not SAMPLE_CATALOG.exists():
        logger.error("Sample catalog not found at %s", SAMPLE_CATALOG)
        return 1
    shutil.copy(SAMPLE_CATALOG, CATALOG_JSONL)
    count = sum(1 for _ in CATALOG_JSONL.open(encoding="utf-8"))
    logger.info("Copied %s sample titles to %s", count, CATALOG_JSONL)
    return 0


def run_scrape(settings: Settings, resume: bool = True) -> int:
    ensure_raw_dir()
    checkpoint = load_checkpoint() if resume else {"scraped_ids": [], "cursor": None}
    already_scraped = set(checkpoint.get("scraped_ids", []))

    client = JustWatchClient(settings)
    started = datetime.now(timezone.utc)
    records: list[dict] = []
    failed = 0

    try:
        for node in iter_catalog(client, settings, page_size=settings.page_size):
            content_id = str(node.get("id") or "")
            if not content_id or content_id in already_scraped:
                continue
            try:
                record = normalize_justwatch_node(node)
                records.append(record)
                already_scraped.add(content_id)
            except Exception as exc:
                failed += 1
                logger.error("Failed to normalize %s: %s", content_id, exc)

            if len(records) % 100 == 0 and records:
                logger.info("Scraped %s titles so far...", len(records))

        if records:
            write_jsonl(records)
            checkpoint["scraped_ids"] = list(already_scraped)
            save_checkpoint(checkpoint)

        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        logger.info(
            "JustWatch scrape complete: %s titles, %s failed, %.1fs → %s",
            len(records),
            failed,
            elapsed,
            CATALOG_JSONL,
        )
        return 0 if records else 1
    except Exception as exc:
        logger.error("JustWatch scrape failed: %s — falling back to sample catalog.", exc)
        return use_sample_catalog()
    finally:
        client.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scrape Disney+ catalog metadata from JustWatch (no subscription required)"
    )
    parser.add_argument("--sample", action="store_true", help="Use bundled sample catalog JSONL")
    parser.add_argument("--fresh", action="store_true", help="Ignore checkpoint and overwrite JSONL")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    settings = Settings.from_env()
    ensure_raw_dir()

    if args.fresh and CATALOG_JSONL.exists():
        CATALOG_JSONL.unlink()
    if args.fresh and CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

    if args.sample:
        return use_sample_catalog()

    return run_scrape(settings, resume=not args.fresh)


if __name__ == "__main__":
    sys.exit(main())
