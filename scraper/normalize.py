"""Normalize raw Disney+ API payloads into catalog records."""

from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from scraper.config import FRANCHISE_OVERRIDES

FRANCHISE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Marvel", ["marvel", "avengers", "spider-man", "spiderman", "x-men", "deadpool", "loki", "wandavision"]),
    ("StarWars", ["star wars", "mandalorian", "ahsoka", "andor", "obi-wan", "skeleton crew"]),
    ("Pixar", ["pixar", "toy story", "finding nemo", "monsters inc", "inside out", "cars", "up", "coco"]),
    ("NatGeo", ["national geographic", "nat geo", "cosmos", "welcome to earth"]),
    ("Star", ["star original", "only murders", "the bear"]),
    ("ESPN", ["espn", "30 for 30", "nfl", "nba", "monday night football"]),
    ("Hulu", ["hulu", "handmaid", "only murders in the building"]),
    ("Disney", ["disney", "mickey", "frozen", "moana", "encanto", "zootopia", "lion king", "aladdin", "mulan", "bluey", "simpson"]),
]

COLLECTION_FRANCHISE_MAP = {
    "marvel": "Marvel",
    "star wars": "StarWars",
    "pixar": "Pixar",
    "national geographic": "NatGeo",
    "disney": "Disney",
    "star": "Star",
    "espn": "ESPN",
    "hulu": "Hulu",
}


def normalize_title(title: str) -> str:
    text = unicodedata.normalize("NFKD", title.lower())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_runtime_minutes(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        minutes = int(value)
        return minutes if minutes > 0 else None
    if isinstance(value, str):
        match = re.search(r"(\d+)", value)
        if match:
            return int(match.group(1))
    return None


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    text = str(value)
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(text.replace("+00:00", "Z"), fmt).date()
        except ValueError:
            continue
    match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
    return date.fromisoformat(match.group(1)) if match else None


def load_franchise_overrides(path: Path = FRANCHISE_OVERRIDES) -> dict[str, str]:
    if not path.exists():
        return {}
    overrides: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            content_id = row.get("content_id", "").strip()
            franchise = row.get("franchise", "").strip()
            if content_id and franchise:
                overrides[content_id] = franchise
    return overrides


def derive_franchise(
    title: str,
    collections: list[str] | None = None,
    content_id: str | None = None,
    overrides: dict[str, str] | None = None,
) -> str:
    if content_id and overrides and content_id in overrides:
        return overrides[content_id]

    haystack = " ".join([title, *(collections or [])]).lower()
    for needle, franchise in COLLECTION_FRANCHISE_MAP.items():
        if needle in haystack:
            return franchise

    for franchise, keywords in FRANCHISE_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return franchise

    return "Other"


def extract_texts(texts: list[dict[str, Any]] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    if not texts:
        return result
    for item in texts:
        if item.get("language") not in (None, "en", "en-US", "en-GB"):
            continue
        field = item.get("field")
        text_type = item.get("type")
        content = item.get("content")
        if field and text_type and content:
            result[f"{field}.{text_type}"] = content
    return result


def map_program_type(program_type: str | None) -> str:
    mapping = {
        "movie": "movie",
        "short": "short",
        "episode": "series",
        "series": "series",
        "sport": "live_sports",
        "sports": "live_sports",
    }
    return mapping.get((program_type or "").lower(), "movie")


def build_disney_url(content_type: str, slug: str | None, content_id: str) -> str | None:
    if not slug:
        return None
    path_type = "movies" if content_type == "movie" else "series"
    return f"https://www.disneyplus.com/{path_type}/{slug}/{content_id}"


def normalize_search_hit(hit: dict[str, Any], scraped_at: datetime | None = None) -> dict[str, Any]:
    """Normalize a search API hit (lighter metadata)."""
    scraped_at = scraped_at or datetime.now(timezone.utc)
    texts = extract_texts(hit.get("texts"))
    title = texts.get("title.full") or hit.get("title") or "Unknown"
    slug = texts.get("title.slug")
    program_type = hit.get("programType") or hit.get("type")
    content_type = map_program_type(program_type)
    family = hit.get("family") or {}
    content_id = (
        hit.get("contentId")
        or hit.get("encodedFamilyId")
        or family.get("encodedFamilyId")
        or family.get("familyId")
        or hit.get("id")
    )
    if not content_id:
        raise ValueError("Search hit missing content_id")

    collections = [
        c.get("name") or c.get("title") or str(c)
        for c in hit.get("collectionGroups", []) or hit.get("collections", []) or []
        if c
    ]
    genres = [g.get("name") or str(g) for g in hit.get("genres", []) or [] if g]

    release_year = hit.get("releaseYear") or hit.get("releases", [{}])[0].get("releaseYear")
    date_added = parse_date(hit.get("startDate") or hit.get("dateAdded"))

    return {
        "content_id": str(content_id),
        "title": title,
        "title_normalized": normalize_title(title),
        "content_type": content_type,
        "release_year": int(release_year) if release_year else None,
        "date_added": date_added.isoformat() if date_added else None,
        "content_rating": hit.get("rating") or hit.get("contentRating"),
        "genres": genres,
        "franchise": derive_franchise(title, collections, str(content_id)),
        "runtime_minutes": parse_runtime_minutes(hit.get("runtimeMillis", 0) // 60000 if hit.get("runtimeMillis") else hit.get("runtime")),
        "season_count": hit.get("seasonCount"),
        "slug": slug,
        "just_watch_url": build_disney_url(content_type, slug, str(content_id)),
        "description": texts.get("description.medium") or texts.get("description.full"),
        "credits": [],
        "original_language": hit.get("originalLanguage"),
        "collections": collections,
        "is_original": hit.get("isOriginal") or hit.get("original") or False,
        "certified_fresh": False,
    }


def normalize_video_bundle(data: dict[str, Any], scraped_at: datetime | None = None) -> dict[str, Any]:
    """Normalize DmcVideoBundle response."""
    scraped_at = scraped_at or datetime.now(timezone.utc)
    video = data.get("video") or data
    texts = extract_texts(video.get("texts"))
    if not texts and video.get("text"):
        text_block = video["text"]
        title = (
            text_block.get("title", {}).get("full", {}).get("program", {}).get("default", {}).get("content")
        )
        description = (
            text_block.get("description", {}).get("medium", {}).get("program", {}).get("default", {}).get("content")
        )
        slug = text_block.get("title", {}).get("slug", {}).get("program", {}).get("default", {}).get("content")
        texts = {
            "title.full": title,
            "description.medium": description,
            "title.slug": slug,
        }

    title = texts.get("title.full") or video.get("title") or "Unknown"
    slug = texts.get("title.slug")
    content_id = video.get("contentId") or video.get("encodedFamilyId") or video.get("familyId")
    releases = video.get("releases") or []
    release_year = releases[0].get("releaseYear") if releases else video.get("releaseYear")
    media = video.get("mediaMetadata") or {}
    genres = [g.get("name") or str(g) for g in video.get("genres", []) or [] if g]
    participants = video.get("participants") or []
    directors = [p.get("name") for p in participants if p.get("role") == "Director" and p.get("name")]
    cast = [p.get("name") for p in participants if p.get("role") in ("Actor", "Starring") and p.get("name")][:10]

    record = normalize_search_hit(
        {
            "contentId": content_id,
            "programType": "movie",
            "texts": [
                {"field": "title", "type": "full", "language": "en", "content": title},
                {"field": "title", "type": "slug", "language": "en", "content": slug},
                {"field": "description", "type": "medium", "language": "en", "content": texts.get("description.medium")},
            ],
            "releaseYear": release_year,
            "genres": genres,
            "mediaMetadata": media,
            "rating": (video.get("rating") or {}).get("value"),
        },
        scraped_at=scraped_at,
    )
    record["credits"] = (
        [{"name": name, "role": "director", "billing_order": i} for i, name in enumerate(directors)]
        + [{"name": name, "role": "cast", "billing_order": i} for i, name in enumerate(cast)]
    )
    record["runtime_minutes"] = parse_runtime_minutes(media.get("runtimeMillis", 0) // 60000 if media.get("runtimeMillis") else media.get("runtime"))
    return record


def normalize_series_bundle(data: dict[str, Any], scraped_at: datetime | None = None) -> dict[str, Any]:
    """Normalize DmcSeriesBundle response."""
    scraped_at = scraped_at or datetime.now(timezone.utc)
    series = data.get("series") or data
    text_block = series.get("text") or {}
    title = (
        text_block.get("title", {}).get("full", {}).get("series", {}).get("default", {}).get("content")
        or series.get("title")
        or "Unknown"
    )
    slug = text_block.get("title", {}).get("slug", {}).get("series", {}).get("default", {}).get("content")
    description = (
        text_block.get("description", {}).get("medium", {}).get("series", {}).get("default", {}).get("content")
    )
    content_id = series.get("seriesId") or series.get("encodedSeriesId") or series.get("contentId")
    seasons = (data.get("seasons") or {}).get("seasons") or data.get("seasons") or []

    genres = [g.get("name") or str(g) for g in series.get("genres", []) or [] if g]
    record = normalize_search_hit(
        {
            "contentId": content_id,
            "programType": "series",
            "texts": [
                {"field": "title", "type": "full", "language": "en", "content": title},
                {"field": "title", "type": "slug", "language": "en", "content": slug},
                {"field": "description", "type": "medium", "language": "en", "content": description},
            ],
            "releaseYear": series.get("releaseYear"),
            "genres": genres,
            "seasonCount": len(seasons) or series.get("seasonCount"),
        },
        scraped_at=scraped_at,
    )
    record["content_type"] = "series"
    record["season_count"] = len(seasons) or series.get("seasonCount")
    return record


def apply_franchise_overrides(record: dict[str, Any], overrides: dict[str, str]) -> dict[str, Any]:
    record["franchise"] = derive_franchise(
        record["title"],
        record.get("collections"),
        record.get("content_id"),
        overrides,
    )
    return record
