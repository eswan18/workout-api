DROP VIEW IF EXISTS v_workouts;

CREATE VIEW v_workouts AS
    SELECT
        w.id AS id,
        w.start_time AS start_time,
        w.end_time AS end_time,
        w.status AS status,
        w.user_id AS user_id,
        w.created_at AS created_at,
        w.updated_at AS updated_at,
        w.deleted_at AS deleted_at,
        wt.id AS workout_type_id,
        wt.name AS workout_type_name,
        wt.notes AS workout_type_notes,
        wt.parent_workout_type_id AS parent_workout_type_id,
        wt.owner_user_id AS workout_type_owner_user_id
    FROM
        workouts w
        LEFT JOIN workout_types wt ON w.workout_type_id = wt.id;