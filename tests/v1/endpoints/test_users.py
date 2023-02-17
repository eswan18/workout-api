from app.v1.models.user import UserOut


def test_get_me_fails_without_auth(client):
    """
    /users/me fails without valid credentials.
    """
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_me_returns_current_user(client, test_user, test_user_auth):
    """
    /users/me returns the corrent user model, with the expected fields.
    """
    response = client.get("/users/me", headers=test_user_auth)
    assert response.status_code == 200
    expected_payload = UserOut.from_orm(test_user)
    actual_payload = UserOut.parse_obj(response.json())
    assert actual_payload == expected_payload
