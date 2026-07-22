"""Migrate legacy catalog records to the current schema."""

from __future__ import annotations

from ingestion.credits import credits_from_record
from scraper.genres import normalize_collections, normalize_genres
from scraper.normalize import derive_franchise, load_franchise_overrides
from scraper.originals import derive_is_original


def migrate_record(record: dict) -> dict:
    """Rename fields and normalize genres/collections for older scrapes."""
    migrated = dict(record)

    if "just_watch_url" not in migrated and "disney_plus_url" in migrated:
        migrated["just_watch_url"] = migrated.pop("disney_plus_url")
    migrated.pop("production_country", None)
    migrated.pop("disney_plus_url", None)
    migrated.pop("episode_count", None)
    migrated.pop("scraped_at", None)
    migrated.pop("media_format", None)
    migrated.pop("directors", None)
    migrated.pop("cast", None)
    migrated.pop("cast_members", None)

    genres = normalize_genres(migrated.get("genres") or [])
    migrated["genres"] = genres

    overrides = load_franchise_overrides()
    franchise = derive_franchise(
        migrated.get("title", ""),
        migrated.get("collections"),
        migrated.get("content_id"),
        overrides,
        genres=genres,
    )
    migrated["franchise"] = franchise
    migrated["collections"] = normalize_collections(franchise, genres)
    migrated["is_original"] = derive_is_original(
        migrated.get("title", ""),
        migrated.get("content_type", "movie"),
        migrated.get("release_year"),
        franchise,
    )
    migrated["certified_fresh"] = bool(migrated.get("certified_fresh"))
    if migrated.get("is_original") is None:
        migrated["is_original"] = False

    if not migrated.get("credits"):
        migrated["credits"] = credits_from_record(record)

    return migrated
