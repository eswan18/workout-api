def test_get_sets_fails_without_auth(client):
    response = client.get("/sets")
    assert response.status_code == 401


def test_get_sets_returns_sets(client, test_user_auth):
    response = client.get("/sets", headers=test_user_auth)
    assert response.status_code == 200
