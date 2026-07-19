"""Tests for Disney+ Original classification."""

from scraper.originals import derive_is_original


def test_derive_is_original_marvel_series():
    assert derive_is_original("Loki", "series", 2021, "Marvel") is True


def test_derive_is_original_theatrical_movie():
    assert derive_is_original("Moana", "movie", 2016, "Disney") is False


def test_derive_is_original_licensed_series():
    assert derive_is_original("The Simpsons", "series", 1989, "Disney") is False
    assert derive_is_original("Bluey", "series", 2018, "Disney") is False
