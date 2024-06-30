DROP TABLE IF EXISTS branches;

CREATE TABLE IF NOT EXISTS branches (
    branch_id TEXT PRIMARY KEY,
    story_id TEXT REFERENCES stories(story_id) ON DELETE CASCADE INITIALLY DEFERRED,
    previous_branch_id TEXT REFERENCES branches(branch_id) ON DELETE SET NULL,
    status TEXT CHECK (status IN ('generating', 'done', 'failed')),
    sentiment TEXT CHECK (sentiment IN ('initial_branch', 'positive', 'negative')),
    audio_url TEXT,
    paragraph TEXT,
    positive_branch_id TEXT REFERENCES branches(branch_id) ON DELETE SET NULL,
    negative_branch_id TEXT REFERENCES branches(branch_id) ON DELETE SET NULL,
    leaf BOOLEAN
);

CREATE INDEX idx_branches_story_id ON branches(story_id);
CREATE INDEX idx_branches_previous_branch_id ON branches(previous_branch_id);
