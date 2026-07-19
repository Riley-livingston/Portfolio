-- Disney+ catalog dimensional model

CREATE TABLE IF NOT EXISTS scrape_runs (
    run_id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    titles_discovered INTEGER DEFAULT 0,
    titles_scraped INTEGER DEFAULT 0,
    titles_failed INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS dis_main (
    content_id VARCHAR(64) PRIMARY KEY,
    title TEXT NOT NULL,
    title_normalized TEXT NOT NULL,
    content_type VARCHAR(32) NOT NULL,
    release_year INTEGER,
    date_added DATE,
    content_rating VARCHAR(32),
    genres TEXT[] DEFAULT '{}',
    franchise VARCHAR(64) NOT NULL DEFAULT 'Other',
    runtime_minutes INTEGER,
    season_count INTEGER,
    slug TEXT,
    just_watch_url TEXT,
    description TEXT,
    original_language TEXT,
    collections TEXT[] DEFAULT '{}',
    is_original BOOLEAN NOT NULL DEFAULT FALSE,
    imdb_rating NUMERIC(3, 1),
    imdb_votes INTEGER,
    rotten_tomatoes_score INTEGER,
    certified_fresh BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_disney_main_franchise ON dis_main (franchise);
CREATE INDEX IF NOT EXISTS idx_disney_main_content_type ON dis_main (content_type);
CREATE INDEX IF NOT EXISTS idx_disney_main_date_added ON dis_main (date_added);
CREATE INDEX IF NOT EXISTS idx_disney_main_release_year ON dis_main (release_year);
CREATE INDEX IF NOT EXISTS idx_disney_main_imdb_rating ON dis_main (imdb_rating);
CREATE INDEX IF NOT EXISTS idx_disney_main_rt_score ON dis_main (rotten_tomatoes_score);

CREATE TABLE IF NOT EXISTS dis_credits (
    credit_id SERIAL PRIMARY KEY,
    content_id VARCHAR(64) NOT NULL REFERENCES dis_main(content_id) ON DELETE CASCADE,
    person_name TEXT NOT NULL,
    role VARCHAR(16) NOT NULL CHECK (role IN ('director', 'cast')),
    billing_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE (content_id, person_name, role)
);

CREATE INDEX IF NOT EXISTS idx_dis_credits_content_id ON dis_credits (content_id);
CREATE INDEX IF NOT EXISTS idx_dis_credits_role ON dis_credits (role);
