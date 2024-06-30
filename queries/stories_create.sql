DROP TABLE IF EXISTS stories;

CREATE TABLE IF NOT EXISTS stories (
    story_id TEXT PRIMARY KEY,
    initial_branch_id TEXT REFERENCES branches(branch_id) ON DELETE SET NULL INITIALLY DEFERRED,
    title TEXT,
    description TEXT,
    initial_prompt TEXT,
    lang TEXT CHECK (lang IN ('en', 'es'))

);

CREATE INDEX idx_stories_initial_branch_id ON stories(initial_branch_id);
