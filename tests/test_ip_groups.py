"""Tests for IP franchise grouping."""

from scraper.ip_groups import match_ip_franchise
from scraper.normalize import derive_franchise


def test_pirates_of_the_caribbean():
    title = "Pirates of the Caribbean: Dead Man's Chest"
    assert derive_franchise(title) == "Pirates of the Caribbean"
    assert match_ip_franchise(title.lower()) == "Pirates of the Caribbean"


def test_lilo_and_stitch():
    assert derive_franchise("Lilo & Stitch") == "Lilo & Stitch"


def test_high_school_musical():
    assert derive_franchise("High School Musical") == "High School Musical"
