from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.sql import select, delete
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import WorkoutType


ROUTE = "/workout_types/"


def test_unauthenticated_user_cant_create_workout_types(
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


def test_authenticated_user_can_create_workout_types(
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
            delete(WorkoutType).where(WorkoutType.id == UUID(resource["id"]))
        )
        session.commit()
        assert result.rowcount == 1


def test_invalid_parent_id_is_rejected(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
):
    payload = postable_payload.copy()
    parent_id = uuid4()
    payload["parent_workout_type_id"] = str(parent_id)
    response = client.post(ROUTE, json=payload, headers=primary_test_user.auth)
    assert response.status_code == 404
    with session_factory() as session:
        # Confirm that no record was added to the database.
        query = select(WorkoutType).where(
            WorkoutType.parent_workout_type_id == parent_id
        )
        record = session.execute(query).scalar()
        assert record is None


def test_user_can_create_workout_type_with_parent_workout_type_thats_public(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    public_workout_type: WorkoutType,
    session_factory: sessionmaker[Session],
):
    # Get the id of a public workout type.
    parent_workout_type_id = public_workout_type.id
    # Try to create a new workout type with that id as the parent.
    payload = postable_payload.copy()
    payload["parent_workout_type_id"] = str(parent_workout_type_id)

    response = client.post(ROUTE, json=payload, headers=secondary_test_user.auth)
    assert response.status_code == 201
    payload = response.json()
    assert len(payload) == 1
    resource = payload[0]

    with session_factory() as session:
        # Clean up and make sure the record is in the db.
        stmt = delete(WorkoutType).where(WorkoutType.id == UUID(resource["id"]))
        result = session.execute(stmt)
        session.commit()
        assert result.rowcount == 1


def test_user_cant_create_workout_type_with_parent_workout_type_thats_owned_by_another_user(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    primary_user_workout_types: WorkoutType,
):
    # Get the id of a workout type that's owned by the primary user.
    parent_workout_type_id = primary_user_workout_types[0].id
    # Try to create a new workout type with that id as the parent, but as the secondary
    # user, who shouldn't be able to view that parent workout type.
    payload = postable_payload.copy()
    payload["parent_workout_type_id"] = str(parent_workout_type_id)

    response = client.post(ROUTE, json=payload, headers=secondary_test_user.auth)
    assert response.status_code == 404
