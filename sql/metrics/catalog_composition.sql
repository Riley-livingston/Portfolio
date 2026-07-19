-- Catalog composition: titles by content type
SELECT
    content_type,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_catalog
FROM dis_main
GROUP BY content_type
ORDER BY title_count DESC;
