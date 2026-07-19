"""Tests for JustWatch normalization."""

from scraper.credits import parse_justwatch_credits
from scraper.justwatch_normalize import map_object_type, normalize_justwatch_node


def test_map_object_type():
    assert map_object_type("MOVIE") == "movie"
    assert map_object_type("SHOW") == "series"


def test_normalize_genres():
    from scraper.genres import normalize_collections, normalize_genres

    assert normalize_genres(["cmy", "drm"]) == ["Comedy", "Drama"]
    assert normalize_genres(["anm", "fml"]) == ["Animation", "Kids & Family"]

    collections = normalize_collections("Marvel", ["Action & Adventure", "Science-Fiction"])
    assert collections == ["Marvel"]

    collections = normalize_collections("Disney", ["Animation", "Kids & Family"])
    assert "Disney" in collections
    assert "Disney Animation" in collections
    assert "Animation" in collections


def test_parse_justwatch_credits_helper():
    credits = parse_justwatch_credits(
        [
            {"role": "DIRECTOR", "name": "Ron Clements"},
            {"role": "ACTOR", "name": "Auli'i Cravalho"},
        ]
    )
    assert credits[0]["role"] == "director"
    assert credits[1]["role"] == "cast"


def test_normalize_justwatch_movie_node():
    node = {
        "id": "tm1645069",
        "objectType": "MOVIE",
        "content": {
            "title": "Moana",
            "originalReleaseYear": 2016,
            "originalReleaseDate": "2016-11-23",
            "runtime": 107,
            "shortDescription": "A spirited teenager sails out on a daring mission.",
            "fullPath": "/us/movie/moana",
            "genres": [{"shortName": "anm"}, {"shortName": "fml"}],
            "ageCertification": "PG",
            "credits": [
                {"role": "DIRECTOR", "name": "Ron Clements"},
                {"role": "DIRECTOR", "name": "John Musker"},
                {"role": "ACTOR", "name": "Auli'i Cravalho"},
                {"role": "ACTOR", "name": "Dwayne Johnson"},
            ],
        },
        "offers": [{"package": {"shortName": "dnp", "clearName": "Disney Plus"}}],
    }
    record = normalize_justwatch_node(node)
    assert record["content_id"] == "tm1645069"
    assert record["title"] == "Moana"
    assert record["content_type"] == "movie"
    assert record["release_year"] == 2016
    assert record["runtime_minutes"] == 107
    assert record["content_rating"] == "PG"
    assert record["genres"] == ["Animation", "Kids & Family"]
    assert any(c["name"] == "Ron Clements" and c["role"] == "director" for c in record["credits"])
    assert any(c["name"] == "Auli'i Cravalho" and c["role"] == "cast" for c in record["credits"])
    assert "justwatch.com" in record["just_watch_url"]
    assert "Disney Animation" in record["collections"]
    assert isinstance(record["is_original"], bool)


def test_certified_fresh_defaults_false():
    node = {
        "id": "tm2",
        "objectType": "MOVIE",
        "content": {"title": "No Score Movie", "originalReleaseYear": 2020},
        "offers": [],
    }
    record = normalize_justwatch_node(node)
    assert record["certified_fresh"] is False
    assert record["credits"] == []


def test_normalize_justwatch_scoring():
    node = {
        "id": "tm1",
        "objectType": "MOVIE",
        "content": {
            "title": "Test Movie",
            "originalReleaseYear": 2020,
            "scoring": {
                "imdbScore": 8.1,
                "imdbVotes": 10000,
                "tomatoMeter": 92,
                "certifiedFresh": True,
            },
        },
        "offers": [],
    }
    record = normalize_justwatch_node(node)
    assert record["imdb_rating"] == 8.1
    assert record["imdb_votes"] == 10000
    assert record["rotten_tomatoes_score"] == 92
    assert record["certified_fresh"] is True
