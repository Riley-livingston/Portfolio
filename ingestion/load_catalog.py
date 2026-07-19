"""Load validated catalog JSONL into PostgreSQL."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

from ingestion.credits import credits_from_record, credits_to_rows
from ingestion.migrate_record import migrate_record
from ingestion.validate import validate_records
from scraper.config import CATALOG_JSONL, CREDITS_TABLE_NAME, SEED_DIR, Settings, quoted_table

logger = logging.getLogger(__name__)

UPSERT_SQL = f"""
INSERT INTO {quoted_table()} (
    content_id, title, title_normalized, content_type, release_year, date_added,
    content_rating, genres, franchise, runtime_minutes, season_count,
    slug, just_watch_url, description,
    original_language, collections, is_original,
    imdb_rating, imdb_votes, rotten_tomatoes_score, certified_fresh,
    updated_at
) VALUES %s
ON CONFLICT (content_id) DO UPDATE SET
    title = EXCLUDED.title,
    title_normalized = EXCLUDED.title_normalized,
    content_type = EXCLUDED.content_type,
    release_year = EXCLUDED.release_year,
    date_added = EXCLUDED.date_added,
    content_rating = EXCLUDED.content_rating,
    genres = EXCLUDED.genres,
    franchise = EXCLUDED.franchise,
    runtime_minutes = EXCLUDED.runtime_minutes,
    season_count = EXCLUDED.season_count,
    slug = EXCLUDED.slug,
    just_watch_url = EXCLUDED.just_watch_url,
    description = EXCLUDED.description,
    original_language = EXCLUDED.original_language,
    collections = EXCLUDED.collections,
    is_original = EXCLUDED.is_original,
    imdb_rating = EXCLUDED.imdb_rating,
    imdb_votes = EXCLUDED.imdb_votes,
    rotten_tomatoes_score = EXCLUDED.rotten_tomatoes_score,
    certified_fresh = EXCLUDED.certified_fresh,
    updated_at = NOW()
"""

CREDITS_INSERT_SQL = f"""
INSERT INTO {CREDITS_TABLE_NAME} (content_id, person_name, role, billing_order)
VALUES %s
ON CONFLICT (content_id, person_name, role) DO UPDATE SET
    billing_order = EXCLUDED.billing_order
"""


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def record_to_row(record: dict) -> tuple:
    date_added = record.get("date_added")
    return (
        record["content_id"],
        record["title"],
        record["title_normalized"],
        record["content_type"],
        record.get("release_year"),
        date_added,
        record.get("content_rating"),
        record.get("genres") or [],
        record.get("franchise", "Other"),
        record.get("runtime_minutes"),
        record.get("season_count"),
        record.get("slug"),
        record.get("just_watch_url") or record.get("disney_plus_url"),
        record.get("description"),
        record.get("original_language"),
        record.get("collections") or [],
        bool(record.get("is_original")),
        record.get("imdb_rating"),
        record.get("imdb_votes"),
        record.get("rotten_tomatoes_score"),
        bool(record.get("certified_fresh")),
        datetime.now(timezone.utc),
    )


def connect(settings: Settings):
    return psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def load_catalog(path: Path | None = None, settings: Settings | None = None) -> dict:
    settings = settings or Settings.from_env()
    source = path or CATALOG_JSONL
    if not source.exists():
        sample = SEED_DIR / "sample_catalog.jsonl"
        if sample.exists():
            logger.warning("Catalog JSONL missing; using sample at %s", sample)
            source = sample
        else:
            raise FileNotFoundError(f"No catalog data at {source}")

    records = [migrate_record(r) for r in read_jsonl(source)]
    valid, invalid = validate_records(records)
    if invalid:
        for record, errors in invalid[:5]:
            logger.warning("Invalid record %s: %s", record.get("content_id"), errors)

    if not valid:
        raise ValueError("No valid records to load")

    rows = [record_to_row(r) for r in valid]
    credit_rows: list[tuple] = []
    content_ids: list[str] = []
    for record in valid:
        content_id = record["content_id"]
        content_ids.append(content_id)
        credit_rows.extend(credits_to_rows(content_id, credits_from_record(record)))

    conn = connect(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scrape_runs (started_at, titles_discovered, titles_scraped, status)
                VALUES (NOW(), %s, %s, 'running') RETURNING run_id
                """,
                (len(records), len(valid)),
            )
            run_id = cur.fetchone()[0]
            execute_values(cur, UPSERT_SQL, rows, page_size=100)
            cur.execute(
                f"DELETE FROM {CREDITS_TABLE_NAME} WHERE content_id = ANY(%s)",
                (content_ids,),
            )
            if credit_rows:
                execute_values(cur, CREDITS_INSERT_SQL, credit_rows, page_size=500)
            cur.execute(
                """
                UPDATE scrape_runs
                SET finished_at = NOW(), titles_failed = %s, status = 'completed'
                WHERE run_id = %s
                """,
                (len(invalid), run_id),
            )
        conn.commit()
    finally:
        conn.close()

    report = {
        "loaded": len(valid),
        "invalid": len(invalid),
        "credits_loaded": len(credit_rows),
        "source": str(source),
    }
    logger.info(
        "Loaded %s titles and %s credits (%s invalid) from %s",
        report["loaded"],
        report["credits_loaded"],
        report["invalid"],
        source,
    )
    return report


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    try:
        load_catalog()
        return 0
    except Exception as exc:
        logger.error("Load failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
