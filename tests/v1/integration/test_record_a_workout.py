import os
from datetime import datetime, timezone

from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.utils import recursive_hard_delete
from app.db.models.user import UserWithAuth

from .client_session import ClientSession


USER_CREATION_SECRET = os.environ["USER_CREATION_SECRET"]


def test_flow(
    client: TestClient,
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
):
    session = ClientSession(client=client, auth=primary_test_user.auth)
    now = datetime.now(tz=timezone.utc)

    # Start a workout.
    workout = session.start_new_workout(time=now)
    return
    # Repeatedly check how many exercises you've done, then record another.
    for i in range(3):
        exes = session.get_exercises_for_workout(workout_id=workout.id)
        assert len(exes) == i
        session.create_new_exercise(workout_id=workout.id)

    # Do two sets of a "new" type of exercise.
    ex_type = session.create_new_ex_type()
    session.create_new_exercise(workout_id=workout.id, exercise_type_id=ex_type.id)
    session.create_new_exercise(workout_id=workout.id, exercise_type_id=ex_type.id)

    # Finish the workout

    # Clean up everything
    recursive_hard_delete(primary_test_user.user, session_factory)
