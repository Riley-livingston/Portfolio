# Disney+ Catalog Scraping Pipeline

Production-grade pipeline to scrape the **Disney+ catalog via [JustWatch](https://www.justwatch.com/us/provider/disney-plus)** (no paid Disney+ account required), load into PostgreSQL, and analyze via SQL + Streamlit dashboard.

## Quick Start

```bash
cp .env.example .env
make setup
make scrape          # fetches ~2,000+ Disney+ titles from JustWatch
make load
make views
make dashboard       # http://localhost:8501
make test
```

Adminer SQL UI: http://localhost:8080 (user: `disney`, password: `disney`, database: `disney_catalog`)

## Why JustWatch?

Disney+ requires a paid subscription to access their internal catalog API. **JustWatch** publicly lists every movie and TV show on Disney+ (~2,000+ titles in the US) and exposes data via their GraphQL API — no login needed.

**Source page:** https://www.justwatch.com/us/provider/disney-plus

## Architecture

```
JustWatch GraphQL → scraper/ → data/raw/disney_catalog.jsonl → ingestion/ → PostgreSQL → SQL views → Streamlit
```

## Field Schema

| Field | Source on JustWatch |
|-------|---------------------|
| content_id | JustWatch node `id` (e.g. `tm123`, `ts456`) |
| title | `content.title` |
| content_type | `MOVIE` → movie, `SHOW` → series |
| release_year | `content.originalReleaseYear` |
| date_added | `originalReleaseDate` (proxy — JustWatch doesn't expose Disney+ add date) |
| content_rating | `content.ageCertification` |
| genres | Normalized labels from `content.genres[].shortName` (e.g. `cmy` → Comedy) |
| franchise | Derived from title + genres |
| runtime_minutes | `content.runtime` |
| season_count | `totalSeasonCount` (series) |
| just_watch_url | JustWatch title URL (links to Disney+ offers) |

Primary Postgres table: `dis_main`.

See [schemas/contracts/catalog_title.json](schemas/contracts/catalog_title.json) for the full schema.

## Commands

| Command | Description |
|---------|-------------|
| `make up` | Start Postgres + Adminer |
| `make scrape` | Scrape full Disney+ catalog from JustWatch |
| `make scrape-sample` | Use bundled 20-title sample (offline dev) |
| `make load` | Validate + load into Postgres |
| `make ingest` | Scrape + load |
| `make migrate` | Migrate existing DB to `dis_main` schema |
| `make dashboard` | Launch Streamlit |
| `make test` | Run pytest |

## Configuration (`.env`)

```env
JUSTWATCH_COUNTRY=US          # ISO country code
JUSTWATCH_LANGUAGE=en
JUSTWATCH_PAGE_SIZE=100       # titles per GraphQL page
RATE_LIMIT_MS=500             # delay between requests
SCRAPE_LIMIT=0                # 0 = full catalog; set to 50 for quick dev test
```

## Scraper Features

- **No subscription** — uses public JustWatch GraphQL API
- **Rate limiting** — configurable delay between pages
- **Checkpoint/resume** — progress saved to `data/raw/scrape_checkpoint.json`
- **Full catalog** — paginates all ~2,088 US Disney+ titles
- **Validation** — JSON schema contract before Postgres load
- **Upsert** — safe to re-run

## Analytics Dashboard

Three Streamlit pages:

1. **Library Overview** — movies vs series, ratings, genres, UHD share
2. **Franchise & Genre** — franchise depth, runtime, originals vs licensed
3. **Catalog Growth** — release decades, freshness scatter

## Scraper Ethics

- Rate limited requests to JustWatch public API
- Catalog metadata only — no personal data
- Unofficial use of JustWatch GraphQL — for portfolio/educational purposes
- Do not hammer the API; respect `RATE_LIMIT_MS`

## Limitations

- Catalog metadata only — no viewership/subscriber data
- `date_added` is proxied from release date (JustWatch doesn't expose Disney+ add dates)
- Episode counts not available from list query (series have `season_count` only)
- Nielsen integration deferred to v2

## Project Structure

```
scraper/
  justwatch_client.py    # JustWatch GraphQL pagination
  justwatch_normalize.py # Map JW nodes → catalog schema
  run.py                 # CLI entry point
ingestion/               # Validate + Postgres load
sql/                     # Metrics + views
dashboard/               # Streamlit app
```
