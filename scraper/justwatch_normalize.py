"""Map JustWatch GraphQL nodes to catalog schema records."""

from __future__ import annotations

from typing import Any

from scraper.credits import parse_justwatch_credits
from scraper.genres import normalize_collections, normalize_genres
from scraper.normalize import (
    apply_franchise_overrides,
    derive_franchise,
    load_franchise_overrides,
    normalize_title,
    parse_date,
)
from scraper.originals import derive_is_original

JUSTWATCH_BASE = "https://www.justwatch.com"


def map_object_type(object_type: str | None) -> str:
    mapping = {
        "MOVIE": "movie",
        "SHOW": "series",
        "SEASON": "series",
        "EPISODE": "series",
    }
    return mapping.get((object_type or "").upper(), "movie")


def has_disney_plus_offer(offers: list[dict[str, Any]] | None) -> bool:
    if not offers:
        return True
    for offer in offers:
        package = offer.get("package") or {}
        short_name = (package.get("shortName") or "").lower()
        clear_name = (package.get("clearName") or "").lower()
        if short_name == "dnp" or "disney" in clear_name:
            return True
    return False


def normalize_justwatch_node(node: dict[str, Any]) -> dict[str, Any]:
    content = node.get("content") or {}
    title = content.get("title") or "Unknown"
    content_id = str(node.get("id") or node.get("objectId"))
    content_type = map_object_type(node.get("objectType"))
    raw_genre_codes = [g.get("shortName") for g in content.get("genres") or [] if g.get("shortName")]
    genres = normalize_genres(raw_genre_codes)
    full_path = content.get("fullPath") or ""
    just_watch_url = f"{JUSTWATCH_BASE}{full_path}" if full_path else None
    slug = full_path.strip("/").split("/")[-1] if full_path else None

    release_date = parse_date(content.get("originalReleaseDate"))
    date_added = release_date
    release_year = content.get("originalReleaseYear")

    overrides = load_franchise_overrides()
    franchise = derive_franchise(title, genres, content_id, overrides)
    collections = normalize_collections(franchise, genres)
    scoring = content.get("scoring") or {}
    credits = parse_justwatch_credits(content.get("credits"))

    record = {
        "content_id": content_id,
        "title": title,
        "title_normalized": normalize_title(title),
        "content_type": content_type,
        "release_year": release_year,
        "date_added": date_added.isoformat() if date_added else None,
        "content_rating": content.get("ageCertification"),
        "genres": genres,
        "franchise": franchise,
        "runtime_minutes": content.get("runtime"),
        "season_count": node.get("totalSeasonCount") if content_type == "series" else None,
        "slug": slug,
        "just_watch_url": just_watch_url,
        "description": content.get("shortDescription"),
        "credits": credits,
        "original_language": "en",
        "collections": collections,
        "is_original": derive_is_original(title, content_type, release_year, franchise),
        "imdb_rating": scoring.get("imdbScore"),
        "imdb_votes": scoring.get("imdbVotes"),
        "rotten_tomatoes_score": scoring.get("tomatoMeter"),
        "certified_fresh": bool(scoring.get("certifiedFresh")),
    }
    return apply_franchise_overrides(record, overrides)


def normalize_justwatch_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for node in nodes:
        if not has_disney_plus_offer(node.get("offers")):
            continue
        records.append(normalize_justwatch_node(node))
    return records
