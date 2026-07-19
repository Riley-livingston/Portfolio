-- Move cast/directors into linked dis_credits table
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

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'dis_main'
          AND column_name = 'directors'
    ) THEN
        INSERT INTO dis_credits (content_id, person_name, role, billing_order)
        SELECT d.content_id, dir.name, 'director', dir.ord - 1
        FROM dis_main d
        CROSS JOIN LATERAL unnest(d.directors) WITH ORDINALITY AS dir(name, ord)
        WHERE d.directors IS NOT NULL AND d.directors <> '{}'
        ON CONFLICT (content_id, person_name, role) DO NOTHING;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'dis_main'
          AND column_name = 'cast_members'
    ) THEN
        INSERT INTO dis_credits (content_id, person_name, role, billing_order)
        SELECT d.content_id, actor.name, 'cast', actor.ord - 1
        FROM dis_main d
        CROSS JOIN LATERAL unnest(d.cast_members) WITH ORDINALITY AS actor(name, ord)
        WHERE d.cast_members IS NOT NULL AND d.cast_members <> '{}'
        ON CONFLICT (content_id, person_name, role) DO NOTHING;
    END IF;
END $$;

ALTER TABLE dis_main DROP COLUMN IF EXISTS directors;
ALTER TABLE dis_main DROP COLUMN IF EXISTS cast_members;
