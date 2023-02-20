from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import WorkoutType


ROUTE = "/workout_types/"


def test_authentication_required_for_delete(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    wt_to_delete = primary_user_workout_types[0]
    params = {"id": wt_to_delete.id}

    # No auth should get a 401.
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
    assert wt_to_delete.deleted_at == None

    # Different user auth should get a 404 because we can't find that workout type.
    response = client.delete(ROUTE, params=params, headers=secondary_test_user.auth)
    assert response.status_code == 404
    assert set(response.json().keys()) == {"detail"}
    assert wt_to_delete.deleted_at == None


def test_cant_delete_public_workout(
    client: TestClient,
    public_workout_type: WorkoutType,
):
    params = {"id": public_workout_type.id}
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
    assert public_workout_type.deleted_at == None
