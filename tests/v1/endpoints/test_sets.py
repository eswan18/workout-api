def test_get_sets_fails_without_auth(client):
    response = client.get("/exercises/")
    assert response.status_code == 401


def test_get_sets_returns_sets(client, primary_test_user):
    response = client.get("/exercises/", headers=primary_test_user.auth)
    assert response.status_code == 200
