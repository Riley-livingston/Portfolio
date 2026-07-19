-- Catalog freshness and growth metrics
SELECT
    DATE_TRUNC('month', date_added) AS month_added,
    COUNT(*) AS titles_added
FROM dis_main
WHERE date_added IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- Median library age (years since release)
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(YEAR FROM CURRENT_DATE) - release_year) AS median_library_age_years
FROM dis_main
WHERE release_year IS NOT NULL;

-- Release year vs date_added lag (months)
SELECT
    content_id,
    title,
    release_year,
    date_added,
    ROUND(
        (DATE_PART('year', AGE(date_added, MAKE_DATE(release_year, 1, 1))) * 12
         + DATE_PART('month', AGE(date_added, MAKE_DATE(release_year, 1, 1))))::numeric,
        1
    ) AS months_release_to_catalog
FROM dis_main
WHERE release_year IS NOT NULL AND date_added IS NOT NULL
ORDER BY months_release_to_catalog DESC
LIMIT 20;
