DROP TABLE branches;

CREATE TABLE IF NOT EXISTS branches (
    branch_id TEXT PRIMARY KEY,
    story_id TEXT,
    previous_branch_id TEXT,
    status TEXT CHECK (status IN ('generating', 'done', 'failed')),
    sentiment TEXT CHECK (sentiment IN ('initial_branch', 'positive', 'negative')),
    audio_url TEXT,
    paragraph TEXT
);
