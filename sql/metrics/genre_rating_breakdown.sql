-- Genre and rating breakdown
SELECT
    UNNEST(genres) AS genre,
    COUNT(*) AS title_count
FROM dis_main
GROUP BY 1
ORDER BY title_count DESC;

-- Rating distribution
SELECT
    COALESCE(content_rating, 'Unknown') AS content_rating,
    COUNT(*) AS title_count
FROM dis_main
GROUP BY 1
ORDER BY title_count DESC;

-- Original vs licensed by franchise
SELECT
    franchise,
    COUNT(*) FILTER (WHERE is_original IS TRUE) AS originals,
    COUNT(*) FILTER (WHERE is_original IS FALSE) AS licensed,
    COUNT(*) FILTER (WHERE is_original IS NULL) AS unknown
FROM dis_main
GROUP BY franchise
ORDER BY originals DESC;
