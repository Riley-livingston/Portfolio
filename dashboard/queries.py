"""Database query helpers for Streamlit dashboard."""

from __future__ import annotations

import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "disney_catalog"),
        user=os.getenv("POSTGRES_USER", "disney"),
        password=os.getenv("POSTGRES_PASSWORD", "disney"),
    )


def query_df(sql: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


def catalog_summary() -> pd.DataFrame:
    return query_df("SELECT * FROM v_catalog_summary")


def franchise_stats() -> pd.DataFrame:
    return query_df("SELECT * FROM v_franchise_stats ORDER BY titles DESC")


def genre_stats() -> pd.DataFrame:
    return query_df("SELECT * FROM v_genre_stats LIMIT 15")


def rating_stats() -> pd.DataFrame:
    return query_df("SELECT * FROM v_rating_stats")


def catalog_growth() -> pd.DataFrame:
    return query_df("SELECT * FROM v_catalog_growth")


def release_decade() -> pd.DataFrame:
    return query_df("SELECT * FROM v_release_decade")


def freshness_data() -> pd.DataFrame:
    return query_df(
        "SELECT title, franchise, release_year, date_added, library_age_years, months_release_to_catalog "
        "FROM v_freshness WHERE date_added IS NOT NULL ORDER BY date_added DESC LIMIT 100"
    )


def franchise_genre_matrix() -> pd.DataFrame:
    return query_df(
        """
        SELECT franchise, genre, COUNT(*)::int AS title_count
        FROM dis_main, UNNEST(genres) AS genre
        GROUP BY franchise, genre
        ORDER BY title_count DESC
        """
    )


def imdb_ratings_scatter() -> pd.DataFrame:
    return query_df(
        """
        SELECT title, franchise, release_year, imdb_rating, imdb_votes
        FROM dis_main
        WHERE imdb_rating IS NOT NULL AND release_year IS NOT NULL
        ORDER BY release_year
        """
    )


def talent_imdb_ratings() -> pd.DataFrame:
    return query_df(
        """
        SELECT
            c.person_name,
            c.role,
            COUNT(DISTINCT c.content_id)::int AS titles,
            ROUND(AVG(m.imdb_rating)::numeric, 2) AS avg_imdb
        FROM dis_credits c
        JOIN dis_main m ON m.content_id = c.content_id
        WHERE m.imdb_rating IS NOT NULL
          AND LENGTH(TRIM(c.person_name)) > 2
        GROUP BY c.person_name, c.role
        HAVING COUNT(DISTINCT c.content_id) >= 3
        ORDER BY avg_imdb DESC, titles DESC
        """
    )
