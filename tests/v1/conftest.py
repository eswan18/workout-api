from string import ascii_letters
from random import choices
from uuid import uuid4
from typing import Iterator
from datetime import datetime, timezone

from sqlalchemy.sql import delete
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient
import pytest

from app.v1 import app
from app import db
from app.db.utils import recursive_hard_delete
from app.db.database import get_session_factory_sync
from app.db.models.user import UserWithAuth
from app.db.models import Exercise, ExerciseType, Workout, WorkoutType
from app.v1.auth import hash_pw, create_jwt_token


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def session_factory() -> sessionmaker[Session]:
    return get_session_factory_sync()


@pytest.fixture(scope="session", autouse=True)
def primary_test_user(session_factory) -> Iterator[UserWithAuth]:
    """
    Create a temporary test user and corresponding auth for the duration of testing.
    """
    # Setup: create a unique, fake user.
    user_string = "".join(choices(ascii_letters, k=15))
    password = "".join(choices(ascii_letters, k=15))
    unique_email = f"testuser1-{user_string}@example.com"
    pw_hash = hash_pw(unique_email, password)
    user = db.User(
        id=uuid4(),
        email=unique_email,
        pw_hash=pw_hash,
    )
    # Insert it in the db.
    with session_factory(expire_on_commit=False) as session:
        session.add(user)
        session.commit()

    token = create_jwt_token(user.email)
    auth_header = {"Authorization": f"Bearer {token.access_token}"}

    yield UserWithAuth(user, auth_header)

    # Teardown: delete from db.
    recursive_hard_delete(user.id, session_factory)


@pytest.fixture(scope="session", autouse=True)
def secondary_test_user(session_factory) -> Iterator[UserWithAuth]:
    """
    Create a temporary test user and corresponding auth for the duration of testing.
    """
    # Setup: create a unique, fake user.
    user_string = "".join(choices(ascii_letters, k=15))
    password = "".join(choices(ascii_letters, k=15))
    unique_email = f"testuser2-{user_string}@example.com"
    pw_hash = hash_pw(unique_email, password)
    user = db.User(
        id=uuid4(),
        email=unique_email,
        pw_hash=pw_hash,
    )
    # Insert it in the db.
    with session_factory(expire_on_commit=False) as session:
        session.add(user)
        session.commit()

    token = create_jwt_token(user.email)
    auth_header = {"Authorization": f"Bearer {token.access_token}"}

    yield UserWithAuth(user, auth_header)

    # Teardown: delete from db.
    recursive_hard_delete(user.id, session_factory)


####################
# Public resources #
####################


@pytest.fixture(scope="function")
def public_exercise_type(
    session_factory: sessionmaker[Session],
) -> Iterator[ExerciseType]:
    """Add a public exercise type to the db."""
    with session_factory(expire_on_commit=False) as session:
        ex = ExerciseType(
            name="a public exercise type",
        )
        session.add(ex)
        session.commit()

    yield ex

    with session_factory() as session:
        session.execute(delete(ExerciseType).where(ExerciseType.id == ex.id))
        session.commit()


@pytest.fixture(scope="function")
def public_workout_type(
    session_factory: sessionmaker[Session],
) -> Iterator[WorkoutType]:
    """Add a public workout type to the db."""
    with session_factory(expire_on_commit=False) as session:
        wt = WorkoutType(
            name="a public workout type",
        )
        session.add(wt)
        session.commit()

    yield wt

    with session_factory() as session:
        session.execute(delete(WorkoutType).where(WorkoutType.id == wt.id))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_workout_and_exercise_type(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
) -> Iterator[tuple[Workout, ExerciseType]]:
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        # Add a workout to record exercises in.
        wkt = Workout(
            start_time=datetime(2023, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
            status="in-progress",
            user_id=user_id,
        )
        # And an exercise type that exercises can be instances of.
        ex_tp = ExerciseType(
            name="Crunches",
            number_of_weights=0,
            owner_user_id=user_id,
        )
        session.add_all([wkt, ex_tp])
        session.commit()

    yield (wkt, ex_tp)

    with session_factory() as session:
        session.execute(delete(Workout).where(Workout.id == wkt.id))
        session.execute(delete(ExerciseType).where(ExerciseType.id == ex_tp.id))
        session.commit()


@pytest.fixture(scope="function")
def secondary_user_workout_and_exercise_type(
    session_factory: sessionmaker[Session],
    secondary_test_user: UserWithAuth,
) -> Iterator[tuple[Workout, ExerciseType]]:
    user_id = secondary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        # Add a workout to record exercises in.
        wkt = Workout(
            start_time=datetime(2023, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
            status="in-progress",
            user_id=user_id,
        )
        # And an exercise type that exercises can be instances of.
        ex_tp = ExerciseType(
            name="Crunches",
            number_of_weights=0,
            owner_user_id=user_id,
        )
        session.add_all([wkt, ex_tp])
        session.commit()

    yield (wkt, ex_tp)

    with session_factory() as session:
        session.execute(delete(Workout).where(Workout.id == wkt.id))
        session.execute(delete(ExerciseType).where(ExerciseType.id == ex_tp.id))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_exercises(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
) -> Iterator[tuple[Exercise, ...]]:
    """Add exercises owned by the primary user to the db."""
    user_id = primary_test_user.user.id
    workout, exercise_type = primary_user_workout_and_exercise_type
    exes = [
        Exercise(
            start_time=datetime(2023, 1, 1, 10, 34, 3, tzinfo=timezone.utc),
            weight=10,
            weight_unit="pounds",
            reps=25,
            notes="My first set of the day",
            exercise_type_id=exercise_type.id,
            workout_id=workout.id,
            user_id=user_id,
        ),
        Exercise(
            start_time=datetime(2023, 1, 1, 10, 35, 55, tzinfo=timezone.utc),
            weight=5,
            weight_unit="pounds",
            reps=22,
            seconds=10,
            exercise_type_id=exercise_type.id,
            workout_id=workout.id,
            user_id=user_id,
        ),
    ]
    with session_factory(expire_on_commit=False) as session:
        session.add_all(exes)
        session.commit()

    yield exes

    with session_factory() as session:
        session.execute(delete(Exercise).where(Exercise.id.in_(row.id for row in exes)))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_exercise_of_different_type_and_workout(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
) -> Iterator[tuple[Workout, ExerciseType, tuple[Exercise, ...]]]:
    """
    Build an exercise that isn't the same type or in the same workout as the others.
    """
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        # Add a workout to record the exercise in.
        wkt = Workout(
            start_time=datetime(2023, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
            status="in-progress",
            user_id=user_id,
        )
        # And an exercise type that the exercise can be an instance of.
        ex_tp = ExerciseType(
            name="Wall-sits",
            number_of_weights=0,
            owner_user_id=user_id,
        )
        session.add_all([wkt, ex_tp])
        session.commit()
        ex = Exercise(
            start_time=datetime(2023, 1, 1, 10, 35, 55, tzinfo=timezone.utc),
            weight=50,
            seconds=60,
            exercise_type_id=ex_tp.id,
            workout_id=wkt.id,
            user_id=user_id,
        )
        session.add(ex)
        session.commit()

    yield (wkt, ex_tp, ex)

    with session_factory() as session:
        session.execute(delete(Exercise).where(Exercise.id == ex.id))
        session.execute(delete(Workout).where(Workout.id == wkt.id))
        session.execute(delete(ExerciseType).where(ExerciseType.id == ex_tp.id))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_soft_deleted_exercise(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: Iterator[tuple[Workout, ExerciseType]],
) -> Iterator[Exercise]:
    user_id = primary_test_user.user.id
    workout, exercise_type = primary_user_workout_and_exercise_type
    with session_factory(expire_on_commit=False) as session:
        ex = Exercise(
            start_time=datetime(2023, 1, 1, 10, 35, 55, tzinfo=timezone.utc),
            weight=0,
            exercise_type_id=exercise_type.id,
            workout_id=workout.id,
            user_id=user_id,
            deleted_at=datetime.now(),
        )
        session.add(ex)
        session.commit()

    yield ex

    with session_factory() as session:
        session.execute(delete(Exercise).where(Exercise.id == ex.id))
        session.commit()
