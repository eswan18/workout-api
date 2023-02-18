from uuid import UUID
import os
from datetime import datetime, timezone
from string import ascii_letters
import random

from sqlalchemy.orm import sessionmaker, Session
from app.db.utils import recursive_hard_delete

from fastapi.testclient import TestClient
from app.db.database import get_session_factory_sync


USER_CREATION_SECRET = os.environ["USER_CREATION_SECRET"]


def test_flow(client: TestClient, session_factory: sessionmaker[Session]):
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
    # Nothing should come back except "email" and "id" -- we want to be sure no
    # password/creds fields are returned.
    assert set(response_payload.keys()) == {"email", "id"}
    my_id = response_payload["id"]

    ###################################################################################
    # You shouldn't have any personal resources, but should be able to see shared ones.
    ###################################################################################
    personal_resource_endpoints = ["/sets/", "/workouts/"]
    for endpoint in personal_resource_endpoints:
        response = client.get(endpoint, headers=auth_header)
        assert response.status_code == 200
        response_payload = response.json()
        assert response_payload == []
    # There should be *some* resources returned in these cases, but none owned by you;
    # only "public" ones that have a null owner field.
    owned_resource_endpoints = ["/exercise_types/", "/workout_types/"]
    for endpoint in owned_resource_endpoints:
        # There should be *some* resources returned in these cases, but none owned by you.
        response = client.get(endpoint, headers=auth_header)
        assert response.status_code == 200
        response_payload = response.json()
        assert isinstance(response_payload, list)
        assert len(response_payload) > 0
        # Make sure that the owner_user_id field is None -- indicating that these are all "public".
        assert all(wt["owner_user_id"] is None for wt in response_payload)

    #################################################
    # Create a new workout type and check it's there.
    #################################################
    new_wkt_tp = {
        "name": "hard work",
        "notes": "pick things up and put em down",
    }
    response = client.post("/workout_types/", headers=auth_header, json=new_wkt_tp)
    assert response.status_code == 201
    response_payload = response.json()
    assert len(response_payload) == 1
    wkt_tp_id = response_payload[0]["id"]
    # Fetch all workout types owned by you. Should be just this one.
    response = client.get(
        "/workout_types/", params={"owner_user_id": my_id}, headers=auth_header
    )
    assert response.status_code == 200
    response_payload = response.json()
    assert isinstance(response_payload, list)
    assert len(response_payload) == 1
    record = response_payload[0]
    assert record == new_wkt_tp | {
        "id": wkt_tp_id,
        "owner_user_id": my_id,
        "parent_workout_type_id": None,
    }

    #################################################
    # Create a new exercise type and check it's there.
    #################################################
    new_ex_tp = {
        "name": "toetouches",
    }
    response = client.post("/exercise_types/", headers=auth_header, json=new_ex_tp)
    assert response.status_code == 201
    response_payload = response.json()
    assert len(response_payload) == 1
    ex_tp_id = response_payload[0]["id"]
    # Fetch all exercises owned by you. Should be just this one.
    response = client.get(
        "/exercise_types/", params={"owner_user_id": my_id}, headers=auth_header
    )
    assert response.status_code == 200
    response_payload = response.json()
    assert isinstance(response_payload, list)
    assert len(response_payload) == 1
    record = response_payload[0]
    assert record == new_ex_tp | {
        "id": ex_tp_id,
        "notes": None,
        "number_of_weights": 1,
        "owner_user_id": my_id,
    }

    ##################################################
    # Create a new workout and a couple of sets in it.
    ##################################################
    new_workout = {
        "start_time": datetime(
            year=2023,
            month=1,
            day=1,
            hour=9,
            minute=30,
            second=0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "end_time": datetime(
            year=2023,
            month=1,
            day=1,
            hour=10,
            minute=15,
            second=0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "status": "in progress",
        "workout_type_id": wkt_tp_id,
    }
    response = client.post("/workouts/", headers=auth_header, json=new_workout)
    assert response.status_code == 201
    response_payload = response.json()
    assert len(response_payload) == 1
    wkt_id = response_payload[0]["id"]
    # Fetch all workouts owned by you -- should be just this one.
    response = client.get("/workouts/", headers=auth_header, params={"user_id": my_id})
    assert response.status_code == 200
    response_payload = response.json()
    assert len(response_payload) == 1
    record = response_payload[0]
    assert record == new_workout | {
        "id": wkt_id,
        "user_id": my_id,
        "notes": None,
    }

    new_sets = [
        {
            "start_time": datetime(
                year=2023,
                month=1,
                day=1,
                hour=9,
                minute=30,
                second=0,
                tzinfo=timezone.utc,
            ).isoformat(),
            "weight": 0,
            "seconds": 60,
            "exercise_type_id": ex_tp_id,
            "workout_id": wkt_id,
        },
        {
            "start_time": datetime(
                year=2023,
                month=1,
                day=1,
                hour=9,
                minute=31,
                second=0,
                tzinfo=timezone.utc,
            ).isoformat(),
            "weight": 0,
            "seconds": 58,
            "exercise_type_id": ex_tp_id,
            "workout_id": wkt_id,
        },
    ]

    set_ids = []
    response = client.post("/sets/", headers=auth_header, json=new_sets)
    assert response.status_code == 201
    response_payload = response.json()
    set_ids = [p["id"] for p in response_payload]
    # Fetch them
    response = client.get("/sets", headers=auth_header, params={"user_id": my_id})
    assert response.status_code == 200
    response_payload = response.json()
    assert len(response_payload) == 2
    assert set(record["id"] for record in response_payload) == set(set_ids)

    # Clean up.
    recursive_hard_delete(UUID(my_id), session_factory)
