"""Heuristics for Disney+ Original classification."""

from __future__ import annotations

from scraper.normalize import normalize_title

DISNEY_PLUS_LAUNCH_YEAR = 2019

ORIGINAL_FRANCHISES = {"Marvel", "StarWars", "NatGeo", "Star", "Hulu"}

LICENSED_SERIES_KEYWORDS = (
    "simpsons",
    "bluey",
    "family guy",
    "bobs burgers",
    "american dad",
    "how i met your mother",
    "modern family",
    "black ish",
    "fresh off the boat",
    "greys anatomy",
    "criminal minds",
    "bones",
    "castle",
    "naruto",
    "suite life",
    "phineas and ferb",
    "gravity falls",
    "kim possible",
    "ducktales",
    "recess",
    "power rangers",
    "full house",
    "home improvement",
    "boy meets world",
    "once upon a time",
    "lost",
    "desperate housewives",
    "scrubs",
    "futurama",
    "king of the hill",
)


def derive_is_original(
    title: str,
    content_type: str,
    release_year: int | None,
    franchise: str,
) -> bool:
    """Estimate whether a title is a Disney+ Original (no direct JW field).

    JustWatch does not expose an original/exclusive flag, so series-first
    originals are inferred from franchise and release timing. Movies default
    to licensed unless they are clearly post-launch franchise series content.
    """
    if content_type != "series":
        return False

    if not release_year or release_year < DISNEY_PLUS_LAUNCH_YEAR:
        return False

    title_norm = normalize_title(title)
    if any(keyword in title_norm for keyword in LICENSED_SERIES_KEYWORDS):
        return False

    if franchise in ORIGINAL_FRANCHISES:
        return True

    if franchise == "Disney" and release_year >= 2020:
        return True

    return False
