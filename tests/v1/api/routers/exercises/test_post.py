from uuid import UUID, uuid4

import pytest
from sqlalchemy.sql import select, delete
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth
from app.db.models import Exercise


ROUTE = "/exercises"


def test_unauthenticated_user_cant_create_exercises(
    client: TestClient, postable_payload: dict[str, str]
):
    # No creds
    response = client.post(ROUTE, json=postable_payload)
    assert response.status_code == 401
    # Wrong creds
    response = client.post(
        ROUTE, json=postable_payload, headers={"Authorization": "Bearer 123456"}
    )
    assert response.status_code == 401


def test_authenticated_user_can_create_exercises(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
):
    response = client.post(ROUTE, json=postable_payload, headers=primary_test_user.auth)
    assert response.status_code == 201
    # Make sure we get the resource back.
    payload = response.json()
    assert len(payload) == 1
    resource = payload[0]
    assert "id" in resource

    # Clean up and make sure that record was in the db.
    with session_factory() as session:
        result = session.execute(
            delete(Exercise).where(Exercise.id == UUID(resource["id"]))
        )
        session.commit()
        assert result.rowcount == 1


def test_invalid_exercise_type_id_is_rejected(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
):
    payload = postable_payload.copy()
    random_id = uuid4()
    payload["exercise_type_id"] = str(random_id)
    response = client.post(ROUTE, json=payload, headers=primary_test_user.auth)
    assert response.status_code == 400
    with session_factory() as session:
        # Confirm that no record was added to the database.
        query = select(Exercise).where(Exercise.exercise_type_id == random_id)
        record = session.execute(query).scalar()
        assert record is None


@pytest.mark.xfail(reason="This check isn't implemented yet.")
def test_user_cant_create_exercise_for_workout_that_isnt_theirs(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
):
    # The postable_payload references a workout_id and exercise_type_id for the primary
    # user.
    response = client.post(
        ROUTE, json=postable_payload, headers=secondary_test_user.auth
    )
    assert response.status_code == 400
