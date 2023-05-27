from string import ascii_letters
from random import choices
from uuid import uuid4
from typing import Iterator

from sqlalchemy.sql import delete
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient
import pytest

from app.v1 import app
from app import db
from app.db.utils import recursive_hard_delete
from app.db.database import get_session_factory_sync
from app.db.models.user import UserWithAuth
from app.db.models import ExerciseType, WorkoutType
from app.v1.auth import hash_pw, create_jwt_payload


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

    jwt = create_jwt_payload(user.email)
    auth_header = {"Authorization": f"Bearer {jwt['access_token']}"}

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

    jwt = create_jwt_payload(user.email)
    auth_header = {"Authorization": f"Bearer {jwt['access_token']}"}

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
