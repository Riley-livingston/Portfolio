"""Credit parsing helpers for scrapers."""

from __future__ import annotations

from typing import Any

CAST_LIMIT = 10


def parse_justwatch_credits(
    raw_credits: list[dict[str, Any]] | None,
    cast_limit: int = CAST_LIMIT,
) -> list[dict[str, Any]]:
    """Map JustWatch credit nodes to catalog credit objects."""
    credits: list[dict[str, Any]] = []
    seen_directors: set[str] = set()
    seen_cast: set[str] = set()
    director_order = 0
    cast_order = 0

    for credit in raw_credits or []:
        name = (credit.get("name") or "").strip()
        if not name:
            continue
        role = (credit.get("role") or "").upper()
        if role == "DIRECTOR" and name not in seen_directors:
            seen_directors.add(name)
            credits.append({"name": name, "role": "director", "billing_order": director_order})
            director_order += 1
        elif role == "ACTOR" and name not in seen_cast and cast_order < cast_limit:
            seen_cast.add(name)
            credits.append({"name": name, "role": "cast", "billing_order": cast_order})
            cast_order += 1

    return credits
