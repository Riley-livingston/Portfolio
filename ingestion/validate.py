"""Validate catalog records against JSON schema contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scraper.config import SCHEMA_PATH


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_record(record: dict[str, Any], validator: Draft202012Validator | None = None) -> list[str]:
    validator = validator or Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(record), key=lambda e: e.path)
    return [f"{'/'.join(map(str, error.path))}: {error.message}" for error in errors]


def validate_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[tuple[dict[str, Any], list[str]]]]:
    validator = Draft202012Validator(load_schema())
    valid: list[dict[str, Any]] = []
    invalid: list[tuple[dict[str, Any], list[str]]] = []
    for record in records:
        errors = validate_record(record, validator)
        if errors:
            invalid.append((record, errors))
        else:
            valid.append(record)
    return valid, invalid
