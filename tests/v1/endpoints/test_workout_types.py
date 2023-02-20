from uuid import UUID
from typing import Iterable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.sql import select, delete
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import WorkoutType

ROUTE = "/workout_types/"


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "name": "Leg dayyyyy",
        "notes": "this is the one you usually skip",
    }


@pytest.fixture(scope="function")
def primary_user_workout_types(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> Iterable[tuple[WorkoutType, WorkoutType]]:
    """Add workout types to the db owned by the primary user."""
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        rows = (
            WorkoutType(
                name="a new workout 1",
                owner_user_id=user_id,
            ),
            WorkoutType(
                name="a new workout 2",
                owner_user_id=user_id,
            ),
        )
        session.add_all(rows)
        session.commit()

    yield rows

    with session_factory() as session:
        session.execute(
            delete(WorkoutType).where(WorkoutType.id.in_(row.id for row in rows))
        )
        session.commit()


#########
# Creates
#########


def test_unauthenticated_user_cant_create_workout_types(
    client: TestClient, postable_payload: dict[str, str]
):
    # No creds
    response = client.post(ROUTE, json=postable_payload)
    assert response.status_code == 401
    # Wrong creds
    response = client.post(
        ROUTE, json=postable_payload, headers={"Authorization": "Bearer 123456"}
    )
    assert response.status_code == 401


def test_authenticated_user_can_create_workout_types(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
):
    response = client.post(ROUTE, json=postable_payload, headers=primary_test_user.auth)
    assert response.status_code == 201
    # Make sure we get the resource back.
    payload = response.json()
    assert len(payload) == 1
    resource = payload[0]
    assert "id" in resource

    # Clean up
    with session_factory() as session:
        session.execute(
            delete(WorkoutType).where(WorkoutType.id == UUID(resource["id"]))
        )
        session.commit()


#########
# Reads
#########


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, WorkoutType],
):
    # Try with no creds.
    response = client.get(ROUTE)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}

    # Try with bad creds.
    bad_user_auth = primary_test_user.auth.copy()
    bad_user_auth.update(Authorization="Bearer 123abc")
    response = client.get(ROUTE, headers=bad_user_auth)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}


def test_one_user_cant_read_anothers_workout_types(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, WorkoutType],
):
    response = client.get(ROUTE, headers=secondary_test_user.auth)
    assert response.status_code == 200
    # Make sure we only get public workout types.
    workout_types = response.json()
    for workout_type in workout_types:
        assert workout_type["owner_user_id"] == None


def test_user_can_read_own_and_public_workout_types(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, WorkoutType],
    session_factory: sessionmaker[Session],
):
    # How many public workouts should there be?
    with session_factory() as session:
        n_public_workout_types = session.scalar(
            select(count(WorkoutType.id)).where(WorkoutType.owner_user_id == None)
        )
    # How many private workouts should there be?
    n_private_workout_types = len(primary_user_workout_types)

    response = client.get(ROUTE, headers=primary_test_user.auth)
    assert response.status_code == 200
    workout_types = response.json()
    assert len(workout_types) == (n_public_workout_types + n_private_workout_types)
    for workout_type in workout_types:
        assert workout_type["owner_user_id"] in (None, str(primary_test_user.user.id))
