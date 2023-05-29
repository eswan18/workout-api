from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.utils import recursive_hard_delete
from app.db.models.user import UserWithAuth
from app.db.models import ExerciseType

from .api_client import ApiClient


def test_flow(
    client: TestClient,
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
    public_exercise_type: ExerciseType,
):
    c = ApiClient(client=client, auth=primary_test_user.auth)
    current_time = datetime.now(tz=timezone.utc)

    # Start a workout.
    workout = c.start_new_workout(time=current_time)

    # Repeatedly check how many exercises you've done, then record another.
    for i in range(3):
        current_time = current_time + timedelta(minutes=2)
        exes = c.get_exercises_for_workout(workout_id=workout.id)
        assert len(exes) == i
        c.create_new_exercise(
            workout_id=workout.id, ex_type_id=public_exercise_type.id, time=current_time
        )

    # Do two sets of a "new" type of exercise.
    current_time = current_time + timedelta(minutes=2)
    ex_type = c.create_new_ex_type()
    c.create_new_exercise(
        workout_id=workout.id, ex_type_id=ex_type.id, time=current_time
    )
    current_time = current_time + timedelta(minutes=2)
    c.create_new_exercise(
        workout_id=workout.id, ex_type_id=ex_type.id, time=current_time
    )

    # Finish the workout.
    current_time = current_time + timedelta(minutes=2)
    c.end_workout(workout_id=workout.id, end_time=current_time)

    # Inspect the state of everything
    exes = c.get_exercises_for_workout(workout_id=workout.id)
    assert len(exes) == 5
    workout = c.get_workout(workout_id=workout.id)
    expected_start_time = current_time - timedelta(minutes=12)
    assert workout.start_time == expected_start_time
    assert workout.end_time == current_time
    assert workout.status == "completed"

    # Clean up everything
    recursive_hard_delete(primary_test_user.user, session_factory)
