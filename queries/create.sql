-- Create the 'branches' table
CREATE TABLE
    branches (
        branch_id TEXT NOT NULL,
        story_id TEXT NOT NULL,
        previous_branch_id TEXT,
        status TEXT NOT NULL,
        sentiment TEXT NOT NULL,
        audio_url TEXT,
        paragraph TEXT,
        positive_branch_id TEXT,
        negative_branch_id TEXT,
        final_branch BOOLEAN NOT NULL DEFAULT false,
        PRIMARY KEY (branch_id),
        CHECK (
            sentiment = ANY (ARRAY['initial_branch', 'positive', 'negative'])
        ),
        CHECK (
            status = ANY (
                ARRAY[
                    'new',
                    'generating-text',
                    'text-only',
                    'generating-audio',
                    'done',
                    'failed'
                ]
            )
        )
    );

-- Create the 'stories' table
CREATE TABLE
    stories (
        story_id TEXT NOT NULL,
        initial_branch_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        initial_prompt TEXT NOT NULL,
        lang TEXT NOT NULL DEFAULT 'en',
        PRIMARY KEY (story_id),
        CONSTRAINT fk_stories_initial_branch FOREIGN KEY (initial_branch_id) REFERENCES branches (branch_id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED
    );

-- Add foreign key constraints to 'branches'
ALTER TABLE branches
ADD CONSTRAINT fk_branches_story FOREIGN KEY (story_id) REFERENCES stories (story_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
ADD CONSTRAINT fk_branches_previous_branch FOREIGN KEY (previous_branch_id) REFERENCES branches (branch_id) ON DELETE SET NULL,
ADD CONSTRAINT fk_branches_positive_branch FOREIGN KEY (positive_branch_id) REFERENCES branches (branch_id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
ADD CONSTRAINT fk_branches_negative_branch FOREIGN KEY (negative_branch_id) REFERENCES branches (branch_id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

-- Create indexes for 'stories' table
CREATE INDEX idx_stories_initial_branch_id ON stories (initial_branch_id);

-- Create indexes for 'branches' table
CREATE INDEX idx_branches_previous_branch_id ON branches (previous_branch_id);

CREATE INDEX idx_branches_story_id ON branches (story_id);