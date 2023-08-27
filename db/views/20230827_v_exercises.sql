DROP VIEW IF EXISTS v_exercises;

CREATE VIEW v_exercises AS
    SELECT
        e.id as id,
        e.start_time as start_time,
        e.weight as weight,
        e.weight_unit as weight_unit,
        e.reps as reps,
        e.seconds as seconds,
        e.notes as notes,
        e.workout_id as workout_id,
        e.user_id as user_id,
        e.created_at as created_at,
        e.updated_at as updated_at,
        e.deleted_at as deleted_at,
        et.id as exercise_type_id,
        et.name as exercise_type_name,
        et.number_of_weights as number_of_weights,
        et.notes as exercise_type_notes,
        et.owner_user_id as exercise_type_owner_user_id
    FROM
        exercises e
        LEFT JOIN exercise_types et ON e.exercise_type_id = et.id;