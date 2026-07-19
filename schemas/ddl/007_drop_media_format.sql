-- Remove unused media_format column
DROP VIEW IF EXISTS v_catalog_summary;
ALTER TABLE dis_main DROP COLUMN IF EXISTS media_format;
