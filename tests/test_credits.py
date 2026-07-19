"""Tests for credit parsing and normalization."""

from ingestion.credits import credits_from_record, credits_to_rows
from scraper.credits import parse_justwatch_credits


def test_parse_justwatch_credits():
    raw = [
        {"role": "DIRECTOR", "name": "Ron Clements"},
        {"role": "DIRECTOR", "name": "John Musker"},
        {"role": "ACTOR", "name": "Auli'i Cravalho"},
        {"role": "ACTOR", "name": "Dwayne Johnson"},
        {"role": "ACTOR", "name": "Auli'i Cravalho"},
    ]
    credits = parse_justwatch_credits(raw)
    assert credits == [
        {"name": "Ron Clements", "role": "director", "billing_order": 0},
        {"name": "John Musker", "role": "director", "billing_order": 1},
        {"name": "Auli'i Cravalho", "role": "cast", "billing_order": 0},
        {"name": "Dwayne Johnson", "role": "cast", "billing_order": 1},
    ]


def test_credits_from_legacy_record():
    record = {
        "directors": ["Ron Clements", "John Musker"],
        "cast": ["Auli'i Cravalho", "Dwayne Johnson"],
    }
    credits = credits_from_record(record)
    assert len(credits) == 4
    assert credits[0]["role"] == "director"
    assert credits[2]["role"] == "cast"


def test_credits_to_rows():
    rows = credits_to_rows(
        "tm1",
        [{"name": "Ron Clements", "role": "director", "billing_order": 0}],
    )
    assert rows == [("tm1", "Ron Clements", "director", 0)]
