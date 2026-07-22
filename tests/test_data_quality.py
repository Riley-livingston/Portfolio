"""Data quality tests for loaded catalog."""

import json
from pathlib import Path

import pytest

from ingestion.validate import validate_records

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "seed" / "sample_catalog.jsonl"


@pytest.fixture
def sample_records():
    records = []
    with SAMPLE.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def test_sample_catalog_validates(sample_records):
    valid, invalid = validate_records(sample_records)
    assert len(valid) >= 15
    assert len(invalid) == 0


def test_required_fields_present(sample_records):
    required = {"content_id", "title", "title_normalized", "content_type", "franchise", "certified_fresh", "credits"}
    for record in sample_records:
        assert required.issubset(record.keys())
        assert isinstance(record["certified_fresh"], bool)
        assert isinstance(record["credits"], list)


def test_franchise_values(sample_records):
    for record in sample_records:
        assert record["franchise"]
        assert len(record["franchise"]) >= 2


def test_content_types(sample_records):
    allowed = {"movie", "series", "short", "live_sports"}
    for record in sample_records:
        assert record["content_type"] in allowed
