def test_get_sets_fails_without_auth(client):
    response = client.get("/sets")
    assert response.status_code == 401


def test_get_sets_returns_sets(client, fake_current_user):
    response = client.get("/sets")
    assert response.status_code == 200
