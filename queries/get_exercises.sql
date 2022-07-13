select
    users.email,
    exercises.name as exercise,
    reps, seconds,
    workouts.start_time as workout_time,
    wt.name as workout_type,
    wt2.name as parent_workout_type
from sets inner join exercises on sets.exercise_id = exercises.id
          inner join workouts on workouts.id = sets.workout_id
          inner join workout_types wt on workouts.workout_type_id = wt.id
          inner join users on users.id = sets.user_id
          left join workout_types wt2 on wt.parent_workout_type_id = wt2.id
;
