-- Backfill is_original and enforce non-null default
UPDATE dis_main SET is_original = COALESCE(is_original, FALSE);

ALTER TABLE dis_main ALTER COLUMN is_original SET DEFAULT FALSE;
ALTER TABLE dis_main ALTER COLUMN is_original SET NOT NULL;
