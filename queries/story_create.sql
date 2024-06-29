CREATE TABLE IF NOT EXISTS story (
    id TEXT PRIMARY KEY,
    initial_branch_id TEXT,
    title TEXT,
    description TEXT,
    initial_prompt TEXT
);
