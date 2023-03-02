import os
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.utils import recursive_hard_delete
from app.db.models.user import UserWithAuth
from app.db.models import ExerciseType

from .client_session import ClientSession


USER_CREATION_SECRET = os.environ["USER_CREATION_SECRET"]


def test_flow(
    client: TestClient,
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
    public_exercise_type: ExerciseType,
):
    session = ClientSession(client=client, auth=primary_test_user.auth)
    now = datetime.now(tz=timezone.utc)

    # Start a workout.
    workout = session.start_new_workout(time=now)

    # Repeatedly check how many exercises you've done, then record another.
    for i in range(3):
        now = now + timedelta(minutes=2)
        exes = session.get_exercises_for_workout(workout_id=workout.id)
        assert len(exes) == i
        session.create_new_exercise(
            workout_id=workout.id, ex_type_id=public_exercise_type.id, time=now
        )

    recursive_hard_delete(primary_test_user.user, session_factory)
    return
    # Do two sets of a "new" type of exercise.
    now = now + timedelta(minutes=2)
    ex_type = session.create_new_ex_type()
    session.create_new_exercise(workout_id=workout.id, ex_type_id=ex_type.id, time=now)
    now = now + timedelta(minutes=2)
    session.create_new_exercise(workout_id=workout.id, ex_type_id=ex_type.id, time=now)

    # Finish the workout

    # Clean up everything
    recursive_hard_delete(primary_test_user.user, session_factory)
