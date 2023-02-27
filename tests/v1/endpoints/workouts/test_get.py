from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth
from app.db import Workout


ROUTE = "/workouts/"


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workouts: tuple[Workout, ...],
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


def test_one_user_cant_read_anothers_workout_types(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workouts: tuple[Workout, ...],
):
    response = client.get(ROUTE, headers=secondary_test_user.auth)
    assert response.status_code == 200
    # This user owns zero workouts.
    workouts = response.json()
    assert len(workouts) == 0


def test_user_can_read_own_workouts(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workouts: tuple[Workout, ...],
    primary_user_soft_deleted_workout: Workout,
):
    """
    Users can read their own workouts but not soft deleted ones.
    """
    response = client.get(ROUTE, headers=primary_test_user.auth)
    assert response.status_code == 200
    workouts = response.json()
    assert len(workouts) == len(primary_user_workouts)
    for workout in workouts:
        assert workout["user_id"] == str(primary_test_user.user.id)


def test_filtering(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workouts: tuple[Workout, ...],
):
    # Get by ID.
    params = {"id": primary_user_workouts[0].id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1

    # Get by status.
    params = {"status": "started"}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    for workout in payload:
        assert workout["status"] == "started"

    # Get by workout type.
    params = {"workout_type_id": primary_user_workouts[0].workout_type_id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    for workout in payload:
        assert workout["workout_type_id"] == str(
            primary_user_workouts[0].workout_type_id
        )
