"""Fetch detailed metadata for discovered Disney+ titles."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from scraper.config import Settings
from scraper.discover import DisneyClient
from scraper.normalize import (
    apply_franchise_overrides,
    load_franchise_overrides,
    normalize_search_hit,
    normalize_series_bundle,
    normalize_video_bundle,
)

logger = logging.getLogger(__name__)


def fetch_title_detail(
    client: DisneyClient,
    meta: dict[str, Any],
    overrides: dict[str, str],
    scraped_at: datetime | None = None,
) -> dict[str, Any]:
    scraped_at = scraped_at or datetime.now(timezone.utc)
    content_id = meta["content_id"]
    program_type = meta.get("program_type", "movie")
    hit = meta.get("hit") or {}

    try:
        if program_type in ("series", "episode"):
            bundle = client.fetch_series_bundle(content_id)
            record = normalize_series_bundle(bundle, scraped_at=scraped_at)
        elif program_type in ("movie", "short"):
            bundle = client.fetch_video_bundle(content_id)
            record = normalize_video_bundle(bundle, scraped_at=scraped_at)
        else:
            record = normalize_search_hit(hit, scraped_at=scraped_at)
    except Exception as exc:
        logger.debug("Detail fetch failed for %s, falling back to search hit: %s", content_id, exc)
        record = normalize_search_hit(hit, scraped_at=scraped_at)

    return apply_franchise_overrides(record, overrides)


def fetch_all_details(
    client: DisneyClient,
    settings: Settings,
    discovered: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    overrides = load_franchise_overrides()
    records: list[dict[str, Any]] = []
    failed: list[str] = []
    scraped_at = datetime.now(timezone.utc)

    items = list(discovered.items())
    if settings.scrape_limit:
        items = items[: settings.scrape_limit]

    for index, (content_id, meta) in enumerate(items, start=1):
        time.sleep(settings.rate_limit_ms / 1000.0)
        try:
            record = fetch_title_detail(client, meta, overrides, scraped_at=scraped_at)
            records.append(record)
            if index % 25 == 0:
                logger.info("Fetched %s/%s titles", index, len(items))
        except Exception as exc:
            logger.error("Failed to fetch %s: %s", content_id, exc)
            failed.append(content_id)

    return records, failed
