CREATE TABLE IF NOT EXISTS branch (
    id TEXT PRIMARY KEY,
    story_id TEXT,
    previous_id TEXT REFERENCES branch(id),
    status TEXT CHECK (status IN ('new', 'generating', 'done', 'failed')),
    audio_url TEXT,
    story TEXT,
    positive_branch_id TEXT,
    negative_branch_id TEXT
);
