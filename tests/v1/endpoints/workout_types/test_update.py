from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import select
from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth
from app.db import WorkoutType

ROUTE = "/workout_types/"


def test_unauthenticated_user_cant_update(
    client: TestClient,
    postable_payload: dict[str, str],
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    wt1 = primary_user_workout_types[0]
    # No creds
    response = client.put(ROUTE, params={"id": wt1.id}, json=postable_payload)
    assert response.status_code == 401
    # Wrong creds
    response = client.put(
        ROUTE, json=postable_payload, headers={"Authorization": "Bearer 123456"}
    )
    assert response.status_code == 401


def test_authenticated_user_can_update(
    client: TestClient,
    postable_payload: dict[str, str],
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
    session_factory: sessionmaker[Session],
):
    wt1 = primary_user_workout_types[0]
    response = client.put(
        ROUTE,
        params={"id": wt1.id},
        json=postable_payload,
        headers=primary_test_user.auth,
    )
    assert response.status_code == 200
    # Make sure the record has been changed in the db.
    with session_factory() as session:
        query = select(WorkoutType).where(WorkoutType.id == wt1.id)
        record = session.execute(query).scalar()
        assert record.id == wt1.id
        assert record.name == postable_payload["name"]
        assert record.notes == postable_payload["notes"]
        assert record.owner_user_id == primary_test_user.user.id
        assert record.parent_workout_type_id is None
        # Hacky way to confirm that the updated_at field was changed.
        assert record.updated_at > record.created_at
