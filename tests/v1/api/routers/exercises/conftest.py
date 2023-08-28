import pytest

from app.db import Workout, ExerciseType


@pytest.fixture(scope="function")
def postable_payload(
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType]
):
    workout, exercise_type = primary_user_workout_and_exercise_type
    return {
        "start_time": "2023-01-01T12:00:00+00:00",
        "weight": 0,
        "reps": 25,
        "exercise_type_id": str(exercise_type.id),
        "workout_id": str(workout.id),
    }
