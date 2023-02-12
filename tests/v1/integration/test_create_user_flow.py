import os
from string import ascii_letters
import random

from fastapi.testclient import TestClient


USER_CREATION_SECRET = os.environ["USER_CREATION_SECRET"]


def test_flow(client: TestClient):
    ####################
    # Create a new user.
    ####################
    # Email addresses must be unique in the db so we need to add some random chars to
    # avoid collisions every time we rerun this test.
    rand_name = "".join(random.choices(ascii_letters, k=10))
    user_email = f"{rand_name}@elendel.gov"
    user_password = "i<3lists"
    payload = {
        "user": {
            "email": user_email,
            "password": user_password,
        },
        "secret": USER_CREATION_SECRET,
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 201, response.content

    #########################
    # Log in with these creds
    #########################
    # Note that this auth has to be passed as form data for some reason.
    login_creds = {
        "username": user_email,
        "password": user_password,
    }
    response = client.post("/token/", data=login_creds)
    assert response.status_code == 201
    response_payload = response.json()
    access_token = response_payload.get("access_token")
    token_type = response_payload.get("token_type")
    assert access_token is not None and token_type is not None
    # Create an auth object that we'll need to use going forward.
    auth_header = {"Authorization": f"Bearer {access_token}"}

    ##################################
    # Check who you are with /users/me
    ##################################
    response = client.get("/users/me", headers=auth_header)
    assert response.status_code == 200
    response_payload = response.json()
    assert response_payload["email"] == user_email
    # Nothing should come back except "email" and "id" -- we want to be sure no password/creds fields are returned.
    assert set(response_payload.keys()) == {"email", "id"}

    ###################################################################################
    # You shouldn't have any personal resources, but should be able to see shared ones.
    ###################################################################################
    personal_resource_endpoints = ["/sets/", "/workouts/"]
    for endpoint in personal_resource_endpoints:
        response = client.get(endpoint, headers=auth_header)
        assert response.status_code == 200
        response_payload = response.json()
        assert response_payload == []
    # There should be *some* resources returned in these cases, but none owned by you.
    shared_resource_endpoints = ["/exercises/", "/workout_types/"]
    for endpoint in shared_resource_endpoints:
        # There should be *some* resources returned in these cases, but none owned by you.
        response = client.get(endpoint, headers=auth_header)
        assert response.status_code == 200
        response_payload = response.json()
        assert isinstance(response_payload, list)
        assert len(response_payload) > 0
