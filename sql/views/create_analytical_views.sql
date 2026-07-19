-- Analytical views for Disney+ catalog dashboard

CREATE OR REPLACE VIEW v_catalog_summary AS
SELECT
    COUNT(*) AS total_titles,
    COUNT(*) FILTER (WHERE content_type = 'movie') AS movie_count,
    COUNT(*) FILTER (WHERE content_type = 'series') AS series_count,
    COUNT(DISTINCT franchise) AS franchise_count,
    ROUND(AVG(runtime_minutes)::numeric, 1) AS avg_runtime_minutes,
    COUNT(*) FILTER (WHERE is_original IS TRUE) AS original_count
FROM dis_main;

DROP VIEW IF EXISTS v_franchise_stats;
CREATE VIEW v_franchise_stats AS
SELECT
    franchise,
    COUNT(*) AS titles,
    ROUND(AVG(runtime_minutes)::numeric, 1) AS avg_runtime_minutes,
    SUM(COALESCE(season_count, 0)) AS total_seasons,
    COUNT(*) FILTER (WHERE is_original IS TRUE) AS originals,
    COUNT(*) FILTER (WHERE is_original IS FALSE) AS licensed
FROM dis_main
GROUP BY franchise;

CREATE OR REPLACE VIEW v_genre_stats AS
SELECT
    genre,
    COUNT(*) AS title_count
FROM dis_main, UNNEST(genres) AS genre
GROUP BY genre
ORDER BY title_count DESC;

CREATE OR REPLACE VIEW v_rating_stats AS
SELECT
    COALESCE(content_rating, 'Unknown') AS content_rating,
    COUNT(*) AS title_count
FROM dis_main
GROUP BY 1
ORDER BY title_count DESC;

CREATE OR REPLACE VIEW v_catalog_growth AS
SELECT
    DATE_TRUNC('month', date_added)::date AS month_added,
    COUNT(*) AS titles_added
FROM dis_main
WHERE date_added IS NOT NULL
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW v_release_decade AS
SELECT
    (release_year / 10) * 10 AS release_decade,
    COUNT(*) AS title_count
FROM dis_main
WHERE release_year IS NOT NULL
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW v_freshness AS
SELECT
    content_id,
    title,
    franchise,
    release_year,
    date_added,
    EXTRACT(YEAR FROM CURRENT_DATE)::int - release_year AS library_age_years,
    CASE
        WHEN release_year IS NOT NULL AND date_added IS NOT NULL THEN
            ROUND(
                (DATE_PART('year', AGE(date_added, MAKE_DATE(release_year, 6, 1))) * 12
                 + DATE_PART('month', AGE(date_added, MAKE_DATE(release_year, 6, 1))))::numeric,
                0
            )
        ELSE NULL
    END AS months_release_to_catalog
FROM dis_main;

CREATE OR REPLACE VIEW v_title_credits AS
SELECT
    c.content_id,
    m.title,
    c.person_name,
    c.role,
    c.billing_order
FROM dis_credits c
JOIN dis_main m USING (content_id)
ORDER BY c.content_id, c.role, c.billing_order;
