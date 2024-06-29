CREATE TABLE IF NOT EXISTS stories (
    story_id TEXT PRIMARY KEY,
    initial_branch_id TEXT,
    title TEXT,
    description TEXT,
    initial_prompt TEXT
);
