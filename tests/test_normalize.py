"""Tests for franchise normalization logic."""

from scraper.normalize import derive_franchise, normalize_title


def test_normalize_title():
    assert normalize_title("The Mandalorian") == "the mandalorian"
    assert normalize_title("Avengers: Endgame!") == "avengers endgame"


def test_derive_franchise_from_collections():
    assert derive_franchise("Random Show", ["Marvel Cinematic Universe"]) == "Marvel"
    assert derive_franchise("A New Hope", ["Star Wars"]) == "StarWars"


def test_derive_franchise_from_title():
    assert derive_franchise("Bluey") == "Disney"
    assert derive_franchise("Shogun", []) == "Other"


def test_franchise_override():
    overrides = {"abc123": "StarWars"}
    assert derive_franchise("Unknown", [], "abc123", overrides) == "StarWars"
