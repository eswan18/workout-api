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
        "status": "started",
        "workout_type_id": None,
    }


@pytest.fixture(scope="function")
def primary_user_workouts(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterator[tuple[Workout, ...]]:
    """Add workouts to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        # Two workouts that are instances of "workout type 1"
        wt1 = WorkoutType(
            name="a new workout type 1",
            owner_user_id=user_id,
        )
        session.add(wt1)
        session.commit()
        w1 = Workout(
            # This one is finished
            start_time=datetime(2023, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 1, 8, 45, 0, tzinfo=timezone.utc),
            status="completed",
            user_id=user_id,
            workout_type_id=wt1.id,
        )
        w2 = Workout(
            # This one is in-progress
            start_time=datetime(2023, 1, 2, 9, 0, 0, tzinfo=timezone.utc),
            end_time=None,
            status="started",
            user_id=user_id,
            workout_type_id=wt1.id,
        )
        session.add(w1)
        session.add(w2)
        session.commit()

        # One workout that is an instance of "workout type 2"
        wt2 = WorkoutType(
            name="a new workout type 2",
            owner_user_id=user_id,
        )
        session.add(wt2)
        session.commit()
        w3 = Workout(
            # This one is finished
            start_time=datetime(2023, 1, 3, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 3, 8, 45, 0, tzinfo=timezone.utc),
            status="completed",
            user_id=user_id,
            workout_type_id=wt2.id,
        )
        session.add(w3)
        session.commit()

    rows = (w1, w2, w3)
    yield rows

    with session_factory() as session:
        session.execute(delete(Workout).where(Workout.id.in_(row.id for row in rows)))
        session.execute(delete(WorkoutType).where(WorkoutType.id.in_((wt1.id, wt2.id))))
        session.commit()


@pytest.fixture(scope="function")
def primary_user_soft_deleted_workout(
    session_factory: sessionmaker[Session],
    primary_test_user: UserWithAuth,
) -> Iterator[Workout]:
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        # Two workouts that are instances of "workout type 1"
        wt = WorkoutType(
            name="a workout type that isn't soft deleted",
            owner_user_id=user_id,
        )
        session.add(wt)
        session.commit()
        w = Workout(
            start_time=datetime(2023, 1, 3, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2023, 1, 3, 8, 45, 0, tzinfo=timezone.utc),
            status="completed",
            user_id=user_id,
            workout_type_id=wt.id,
            deleted_at=datetime(2023, 2, 1, 8, 45, 0, tzinfo=timezone.utc),
        )
        session.add(w)
        session.commit()

    yield w

    with session_factory() as session:
        session.execute(delete(Workout).where(Workout.id == w.id))
        session.commit()
