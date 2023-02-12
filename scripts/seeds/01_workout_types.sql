INSERT INTO workout_types (id, name, notes, parent_workout_type_id, owner_user_id) VALUES
('3d531b3b-907f-488b-b2b6-ad3e541d08fd', 'Upper Body', 'Upper body exercises', NULL, NULL),
('72c29956-f71a-4e6a-b8e2-d6ea2008ed35', 'Pull Day', 'Biceps and upper back exercises', '3d531b3b-907f-488b-b2b6-ad3e541d08fd', NULL),
('a4f69cd3-12ba-42ec-8ffc-b03a167f489e', 'Push Day', 'Chest, shoulders, and triceps exercises', '3d531b3b-907f-488b-b2b6-ad3e541d08fd', NULL),
('463b07e1-4185-4a8f-8b59-71192dc141c4', 'Dumbbells for Dummy', 'Dummys own personal workout', '3d531b3b-907f-488b-b2b6-ad3e541d08fd', 'ddf909e8-1ef9-4cdc-8476-732137a352d8')
;
