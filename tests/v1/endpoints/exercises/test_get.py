from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth
from app.db import Exercise


ROUTE = "/exercises/"


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
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
