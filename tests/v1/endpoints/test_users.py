def test_get_me_fails_without_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401
