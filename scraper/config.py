"""Scraper configuration loaded from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SEED_DIR = ROOT / "data" / "seed"
CATALOG_JSONL = RAW_DIR / "disney_catalog.jsonl"
CHECKPOINT_FILE = RAW_DIR / "scrape_checkpoint.json"
FRANCHISE_OVERRIDES = SEED_DIR / "franchise_overrides.csv"
SCHEMA_PATH = ROOT / "schemas" / "contracts" / "catalog_title.json"

JUSTWATCH_PROVIDER_URL = "https://www.justwatch.com/us/provider/disney-plus"
TABLE_NAME = "dis_main"
CREDITS_TABLE_NAME = "dis_credits"


def quoted_table() -> str:
    return TABLE_NAME


@dataclass(frozen=True)
class Settings:
    justwatch_country: str
    justwatch_language: str
    rate_limit_ms: int
    max_retries: int
    scrape_limit: int
    page_size: int
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            justwatch_country=os.getenv("JUSTWATCH_COUNTRY", "US").upper(),
            justwatch_language=os.getenv("JUSTWATCH_LANGUAGE", "en").lower(),
            rate_limit_ms=int(os.getenv("RATE_LIMIT_MS", "500")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            scrape_limit=int(os.getenv("SCRAPE_LIMIT", "0")),
            page_size=int(os.getenv("JUSTWATCH_PAGE_SIZE", "100")),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "disney_catalog"),
            postgres_user=os.getenv("POSTGRES_USER", "disney"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", "disney"),
        )


def ensure_raw_dir() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
