-- Insert test data for story of a prince
INSERT INTO story (id, initial_branch_id, title, description, initial_prompt) VALUES
('1', '1', 'The Prince', 'A story about a brave prince', 'Once upon a time, there was a brave prince...');

INSERT INTO branch (id, story_id, previous_id, status, audio_url, story, positive_branch_id, negative_branch_id) VALUES
('1', '1', NULL, 'done', 'audio1.wav', 'The prince set out on a journey to find a dragon.', '2', '3'),
('2', '1', '1', 'done', 'audio2.wav', 'The prince found the dragon and fought bravely.', NULL, NULL),
('3', '1', '2', 'done', 'audio3.wav', 'The prince decided to return home and prepare better.', NULL, NULL);

-- Insert test data for story of a duck
INSERT INTO story (id, initial_branch_id, title, description, initial_prompt) VALUES
('2', '4', 'The Duck', 'A story about a curious duck', 'Once upon a time, there was a curious duck...');

INSERT INTO branch (id, story_id, previous_id, status, audio_url, story, positive_branch_id, negative_branch_id) VALUES
('4', '2', NULL, 'done', 'audio4.wav', 'The duck decided to explore the nearby pond.', '5', '6'),
('5', '2', '4', 'done', 'audio5.wav', 'The duck found a new friend in the pond.', NULL, NULL),
('6', '2', '5', 'done', 'audio6.wav', 'The duck got lost and had to find its way back home.', NULL, NULL);
