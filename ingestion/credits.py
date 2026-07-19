"""Credit row helpers for catalog ingestion."""

from __future__ import annotations

from typing import Any


def credits_from_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize credits from a catalog record (new or legacy format)."""
    if record.get("credits"):
        return normalize_credit_list(record["credits"])

    credits: list[dict[str, Any]] = []
    for billing_order, name in enumerate(record.get("directors") or []):
        person = (name or "").strip()
        if person:
            credits.append({"name": person, "role": "director", "billing_order": billing_order})
    for billing_order, name in enumerate(record.get("cast") or record.get("cast_members") or []):
        person = (name or "").strip()
        if person:
            credits.append({"name": person, "role": "cast", "billing_order": billing_order})
    return credits


def normalize_credit_list(credits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, credit in enumerate(credits):
        name = (credit.get("name") or "").strip()
        if not name:
            continue
        role = (credit.get("role") or "").lower()
        if role not in {"director", "cast"}:
            continue
        normalized.append(
            {
                "name": name,
                "role": role,
                "billing_order": credit.get("billing_order", index),
            }
        )
    return normalized


def credits_to_rows(content_id: str, credits: list[dict[str, Any]]) -> list[tuple]:
    return [
        (content_id, credit["name"], credit["role"], credit.get("billing_order", index))
        for index, credit in enumerate(credits)
    ]
