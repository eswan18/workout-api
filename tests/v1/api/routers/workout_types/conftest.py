from datetime import datetime
from typing import Iterator

from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker, Session
import pytest

from app.db.models.user import UserWithAuth
from app.db import WorkoutType


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "name": "Leg dayyyyy",
        "notes": "this is the one you usually skip",
    }


@pytest.fixture(scope="function")
def primary_user_workout_types(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterator[tuple[WorkoutType, ...]]:
    """Add workout types to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        wt1 = WorkoutType(
            name="a new workout type 1",
            owner_user_id=user_id,
        )
        session.add(wt1)
        session.commit()
        # Another workout, child of workout type 1.
        wt2 = WorkoutType(
            name="a new workout type 2",
            owner_user_id=user_id,
            parent_workout_type_id=wt1.id,
        )
        session.add(wt2)
        session.commit()

    rows = (wt1, wt2)
    yield rows

    with session_factory() as session:
        session.execute(
            delete(WorkoutType).where(WorkoutType.id.in_(row.id for row in rows))
        )
        session.commit()


@pytest.fixture(scope="function")
def primary_user_soft_deleted_workout_type(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterator[WorkoutType]:
    """Add a soft-deleted workout type to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        sd_wt = WorkoutType(
            name="a deleted workout type",
            owner_user_id=user_id,
            deleted_at=datetime(year=2023, month=1, day=1),
        )
        session.add(sd_wt)
        session.commit()

    yield sd_wt

    with session_factory() as session:
        session.execute(delete(WorkoutType).where(WorkoutType.id == sd_wt.id))
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
