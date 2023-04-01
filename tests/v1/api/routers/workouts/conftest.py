from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker, Session
import pytest

from app.db.models.user import UserWithAuth
from app.db import WorkoutType, Workout


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "start_time": "2022-01-01T09:30:00",
        "end_time": None,
        "status": "paused",
        "workout_type_id": None,
    }


@pytest.fixture(scope="function")
def primary_user_workout_type(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterator[WorkoutType]:
    """Add a workout type to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        wt = WorkoutType(
            name="a new workout type",
            owner_user_id=user_id,
        )
        session.add(wt)
        session.commit()

    yield wt

    with session_factory() as session:
        session.execute(delete(WorkoutType).where(WorkoutType.id == wt.id))
        session.commit()


@pytest.fixture(scope="function")
def secondary_user_workout_type(
    session_factory: sessionmaker[Session], secondary_test_user: UserWithAuth
) -> Iterator[WorkoutType]:
    """Add a workout type to the db owned by the primary user."""
    user_id = secondary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        wt = WorkoutType(
            name="a new workout type for the secondary user",
            owner_user_id=user_id,
        )
        session.add(wt)
        session.commit()

    yield wt

    with session_factory() as session:
        session.execute(delete(WorkoutType).where(WorkoutType.id == wt.id))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_workouts(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
    primary_user_workout_type: WorkoutType,
    public_workout_type: WorkoutType,
) -> Iterator[tuple[Workout, ...]]:
    """Add workouts to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        w1 = Workout(
            # This one is finished
            start_time=datetime(2023, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 1, 8, 45, 0, tzinfo=timezone.utc),
            status="completed",
            user_id=user_id,
            workout_type_id=primary_user_workout_type.id,
        )
        w2 = Workout(
            # This one is in-progress
            start_time=datetime(2023, 1, 2, 9, 0, 0, tzinfo=timezone.utc),
            end_time=None,
            status="in-progress",
            user_id=user_id,
            workout_type_id=primary_user_workout_type.id,
        )
        session.add(w1)
        session.add(w2)
        session.commit()

        # One workout that is an instance of a public workout type.
        w3 = Workout(
            # This one is finished
            start_time=datetime(2023, 1, 3, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 3, 8, 45, 0, tzinfo=timezone.utc),
            status="completed",
            user_id=user_id,
            workout_type_id=public_workout_type.id,
        )
        session.add(w3)
        session.commit()

    rows = (w1, w2, w3)
    yield rows

    with session_factory() as session:
        session.execute(delete(Workout).where(Workout.id.in_(row.id for row in rows)))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_soft_deleted_workout(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
    primary_user_workout_type: WorkoutType,
) -> Iterator[Workout]:
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        w = Workout(
            start_time=datetime(2023, 1, 3, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 3, 8, 45, 0, tzinfo=timezone.utc),
            status="completed",
            user_id=user_id,
            workout_type_id=primary_user_workout_type.id,
            deleted_at=datetime(2023, 2, 1, 8, 45, 0, tzinfo=timezone.utc),
        )
        session.add(w)
        session.commit()

    yield w

    with session_factory() as session:
        session.execute(delete(Workout).where(Workout.id == w.id))
        session.commit()
