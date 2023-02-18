from fastapi.testclient import TestClient

from app.v1.models.user import UserOut
from app.db.models.user import UserWithAuth


def test_get_me_fails_without_auth(client: TestClient):
    """
    /users/me fails without valid credentials.
    """
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_me_returns_current_user(
    client: TestClient, primary_test_user: UserWithAuth
):
    """
    /users/me returns the corrent user model, with the expected fields.
    """
    response = client.get("/users/me", headers=primary_test_user.auth)
    assert response.status_code == 200
    expected_payload = UserOut.from_orm(primary_test_user.user)
    actual_payload = UserOut.parse_obj(response.json())
    assert actual_payload == expected_payload
