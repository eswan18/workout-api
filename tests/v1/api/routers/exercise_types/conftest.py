from datetime import datetime
from typing import Iterator

import pytest
from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import ExerciseType


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "name": "Sumo deadlifts",
    }


@pytest.fixture(scope="function")
def primary_user_exercise_types(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterator[tuple[ExerciseType, ...]]:
    """Add exercise types to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        ex1 = ExerciseType(
            name="Pull-ups",
            notes="pull yourself up",
            owner_user_id=user_id,
        )
        # Another workout, child of workout type 1.
        ex2 = ExerciseType(
            name="Chin-ups",
            owner_user_id=user_id,
        )
        rows = [ex1, ex2]
        session.add_all(rows)
        session.commit()

    yield rows

    with session_factory() as session:
        session.execute(
            delete(ExerciseType).where(ExerciseType.id.in_(row.id for row in rows))
        )
        session.commit()


@pytest.fixture(scope="function")
def primary_user_soft_deleted_exercise_type(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterator[ExerciseType]:
    """Add a soft-deleted exercise type to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        ex = ExerciseType(
            name="a deleted exercise type",
            owner_user_id=user_id,
            deleted_at=datetime(year=2023, month=1, day=1),
        )
        session.add(ex)
        session.commit()

    yield ex

    with session_factory() as session:
        session.execute(delete(ExerciseType).where(ExerciseType.id == ex.id))
        session.commit()


@pytest.fixture(scope="function")
def public_exercse_type(
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
