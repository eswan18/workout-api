import pytest


ROUTE = "/workout_types/"


@pytest.fixture(scope="function")
def postable_payload():
    return {
        "name": "Leg dayyyyy",
        "notes": "this is the one you usually skip",
    }


def test_unauthenticated_user_cant_create_workouts(client, postable_payload):
    response = client.post(ROUTE, json=postable_payload)
    assert response.status_code == 401


def test_authenticated_user_can_create_workouts(
    client, test_user_auth, postable_payload
):
    response = client.post(ROUTE, json=postable_payload, headers=test_user_auth)
    assert response.status_code == 201
