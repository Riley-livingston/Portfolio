"""JustWatch genre code normalization."""

from __future__ import annotations

# Source: https://apis.justwatch.com/content/genres/locale/en_US
GENRE_MAP: dict[str, str] = {
    "act": "Action & Adventure",
    "ani": "Animation",
    "anm": "Animation",
    "cmy": "Comedy",
    "crm": "Crime",
    "doc": "Documentary",
    "drm": "Drama",
    "fnt": "Fantasy",
    "hst": "History",
    "hrr": "Horror",
    "fml": "Kids & Family",
    "msc": "Music & Musical",
    "trl": "Mystery & Thriller",
    "rma": "Romance",
    "scf": "Science-Fiction",
    "spt": "Sport",
    "war": "War & Military",
    "wsn": "Western",
    "rly": "Reality TV",
    "eur": "Made in Europe",
}


def normalize_genres(codes: list[str] | None) -> list[str]:
    """Map JustWatch short genre codes to readable labels."""
    if not codes:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for code in codes:
        key = (code or "").strip().lower()
        if not key:
            continue
        label = GENRE_MAP.get(key, code.strip().title())
        if label not in seen:
            seen.add(label)
            normalized.append(label)
    return normalized


def normalize_collections(franchise: str, genres: list[str]) -> list[str]:
    """Derive readable Disney+ collection labels from franchise and genres."""
    collections: list[str] = []
    seen: set[str] = set()

    def add(label: str) -> None:
        if label and label not in seen:
            seen.add(label)
            collections.append(label)

    franchise_collections = {
        "Marvel": "Marvel",
        "StarWars": "Star Wars",
        "Pixar": "Pixar",
        "NatGeo": "National Geographic",
        "ESPN": "ESPN",
        "Hulu": "Hulu",
        "Star": "Star Originals",
        "Disney": "Disney",
        "20th Century Studios": "20th Century",
        "Disney Channel": "Disney Channel",
        "Pirates of the Caribbean": "Disney Live Action",
        "Indiana Jones": "Lucasfilm",
        "Winnie the Pooh": "Disney Animation",
        "Classic Disney Animation": "Disney Animation",
        "Princess Stories": "Disney Princess",
    }
    if franchise in franchise_collections:
        add(franchise_collections[franchise])

    genre_collections = {
        "Animation": "Animation",
        "Kids & Family": "Kids & Family",
        "Documentary": "Documentary",
        "Sport": "Sports",
        "Music & Musical": "Music",
    }
    for genre in genres:
        if genre in genre_collections:
            add(genre_collections[genre])

    if franchise == "Disney" and "Animation" in genres:
        add("Disney Animation")

    if not collections:
        add("General")

    return collections
