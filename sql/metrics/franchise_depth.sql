-- Franchise depth analysis
SELECT
    franchise,
    COUNT(*) AS titles,
    ROUND(AVG(runtime_minutes)::numeric, 1) AS avg_runtime_minutes,
    SUM(COALESCE(season_count, 0)) AS total_seasons,
    SUM(CASE WHEN content_type = 'movie' THEN 1 ELSE 0 END) AS movies,
    SUM(CASE WHEN content_type = 'series' THEN 1 ELSE 0 END) AS series
FROM dis_main
GROUP BY franchise
ORDER BY titles DESC;
