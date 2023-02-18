import pytest
from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth


ROUTE = "/workout_types/"


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "name": "Leg dayyyyy",
        "notes": "this is the one you usually skip",
    }


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
