import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import User, UserWithAuth
from app.db import WorkoutType


ROUTE = "/workout_types/"


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "name": "Leg dayyyyy",
        "notes": "this is the one you usually skip",
    }


@pytest.fixture(scope="function")
def wts_in_db(
    session_factory: sessionmaker[Session], primary_test_user: UserWithAuth
) -> User:
    user_id = primary_test_user.user.id
    with session_factory(expire_on_commit=False) as session:
        rows = [
            WorkoutType(
                name="a new workout 1",
                owner_user_id=user_id,
            ),
            WorkoutType(
                name="a new workout 2",
                owner_user_id=None,
            ),
        ]
        session.add_all(rows)
        session.commit()
    return rows


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
):
    response = client.post(ROUTE, json=postable_payload, headers=primary_test_user.auth)
    assert response.status_code == 201
    # Make sure we get the resource back.
    payload = response.json()
    assert len(payload) == 1
    resource = payload[0]
    assert "id" in resource


#########
# Reads
#########


def test_unauthenticated_user_cant_read(
    client: TestClient,
    postable_payload: dict[str, str],
    primary_test_user: UserWithAuth,
):
    # Try with no creds.
    response = client.post(ROUTE, json=postable_payload)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}

    # Try with bad creds.
    bad_user_auth = primary_test_user.auth
    bad_user_auth.update(Authorization="Bearer 123abc")
    response = client.post(ROUTE, json=postable_payload, headers=bad_user_auth)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
