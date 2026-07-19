-- Migrate existing dim_content installs to dis_main schema
DO $$
BEGIN
    IF to_regclass('public.dim_content') IS NOT NULL
       AND to_regclass('public.dis_main') IS NULL THEN
        ALTER TABLE dim_content RENAME TO dis_main;
    END IF;
END $$;

DO $$
BEGIN
    IF to_regclass('public."Disney+ main"') IS NOT NULL
       AND to_regclass('public.dis_main') IS NULL THEN
        ALTER TABLE "Disney+ main" RENAME TO dis_main;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'dis_main'
          AND column_name = 'disney_plus_url'
    ) THEN
        ALTER TABLE dis_main RENAME COLUMN disney_plus_url TO just_watch_url;
    END IF;
END $$;

ALTER TABLE dis_main DROP COLUMN IF EXISTS production_country;

ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS imdb_rating NUMERIC(3, 1);
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS imdb_votes INTEGER;
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS rotten_tomatoes_score INTEGER;
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS certified_fresh BOOLEAN;

CREATE INDEX IF NOT EXISTS idx_dis_main_imdb_rating ON dis_main (imdb_rating);
CREATE INDEX IF NOT EXISTS idx_dis_main_rt_score ON dis_main (rotten_tomatoes_score);
