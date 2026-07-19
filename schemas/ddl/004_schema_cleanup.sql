-- Drop views that reference removed columns (recreated by make views)
DROP VIEW IF EXISTS v_franchise_stats;

ALTER TABLE dis_main DROP COLUMN IF EXISTS episode_count;
ALTER TABLE dis_main DROP COLUMN IF EXISTS scraped_at;

UPDATE dis_main SET certified_fresh = COALESCE(certified_fresh, FALSE);

ALTER TABLE dis_main ALTER COLUMN certified_fresh SET DEFAULT FALSE;
ALTER TABLE dis_main ALTER COLUMN certified_fresh SET NOT NULL;
