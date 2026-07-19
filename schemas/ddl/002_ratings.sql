-- Legacy migration: add rating columns (superseded by 003 for existing DBs)
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS imdb_rating NUMERIC(3, 1);
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS imdb_votes INTEGER;
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS rotten_tomatoes_score INTEGER;
ALTER TABLE dis_main ADD COLUMN IF NOT EXISTS certified_fresh BOOLEAN;

CREATE INDEX IF NOT EXISTS idx_dis_main_imdb_rating ON dis_main (imdb_rating);
CREATE INDEX IF NOT EXISTS idx_dis_main_rt_score ON dis_main (rotten_tomatoes_score);
