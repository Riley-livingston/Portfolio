"""Tests for legacy record migration."""

from ingestion.migrate_record import migrate_record


def test_migrate_legacy_fields():
    record = {
        "content_id": "tm1",
        "title": "Avengers: Endgame",
        "title_normalized": "avengers endgame",
        "content_type": "movie",
        "franchise": "Marvel",
        "genres": ["act", "scf"],
        "disney_plus_url": "https://www.justwatch.com/us/movie/test",
        "production_country": "United States",
        "collections": ["act", "scf"],
        "episode_count": 10,
        "scraped_at": "2026-07-19T12:00:00+00:00",
        "directors": ["Anthony Russo"],
        "cast": ["Robert Downey Jr."],
        "certified_fresh": False,
    }
    migrated = migrate_record(record)
    assert migrated["just_watch_url"] == "https://www.justwatch.com/us/movie/test"
    assert "disney_plus_url" not in migrated
    assert "production_country" not in migrated
    assert "episode_count" not in migrated
    assert "scraped_at" not in migrated
    assert "directors" not in migrated
    assert "cast" not in migrated
    assert migrated["genres"] == ["Action & Adventure", "Science-Fiction"]
    assert migrated["franchise"] == "Marvel"
    assert migrated["collections"] == ["Marvel"]
    assert migrated["certified_fresh"] is False
    assert len(migrated["credits"]) == 2
