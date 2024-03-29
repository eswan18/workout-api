from uuid import uuid4

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
    response = client.patch(ROUTE, params={"id": wt1.id}, json=postable_payload)
    assert response.status_code == 401
    # Wrong creds
    response = client.patch(
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
    response = client.patch(
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


def test_invalid_parent_id_is_rejected(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    wt1 = primary_user_workout_types[0]
    wt1_id, wt1_name = wt1.id, wt1.name
    payload = postable_payload.copy()
    parent_id = uuid4()
    payload["parent_workout_type_id"] = str(parent_id)
    response = client.patch(
        ROUTE, params={"id": wt1_id}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 404
    with session_factory() as session:
        # Confirm that the record wasn't modified.
        query = select(WorkoutType).where(WorkoutType.id == wt1.id)
        record = session.execute(query).scalars().one()
        assert record.name == wt1_name


def test_partial_payload_is_accepted(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    """
    Omitting mandatory fields of a workout type is fine on PATCH.
    """
    wt1 = primary_user_workout_types[0]
    payload = {"notes": postable_payload["notes"]}
    response = client.patch(
        ROUTE, params={"id": wt1.id}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 200
    with session_factory() as session:
        # Confirm that the record was modified.
        query = select(WorkoutType).where(WorkoutType.id == wt1.id)
        record = session.execute(query).scalars().one()
        assert record.notes == payload["notes"]


def test_user_can_set_parent_workout_type_to_a_public_one(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
    public_workout_type: WorkoutType,
    postable_payload: dict[str, str],
):
    """
    Users can update a workout type to set its parent to a public one.

    Since we have a test that setting a workout type to one owned by another user isn't
    allowed, this test is a good check to be sure we're not disallowing public workout
    types as well.
    """
    # Get a workout owned by the primary user.
    wt = primary_user_workout_types[1]
    # Try to update the workout's type to one owned by the secondary user.
    payload = postable_payload.copy()
    payload["parent_workout_type_id"] = str(public_workout_type.id)
    response = client.put(
        ROUTE, params={"id": str(wt.id)}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 200


def test_user_cant_set_parent_workout_type_to_one_owned_by_another_user(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
    secondary_user_workout_type: WorkoutType,
    postable_payload: dict[str, str],
):
    """Users can't update a workout type to set its parent to one owned by another user."""
    # Get a workout owned by the primary user.
    wt = primary_user_workout_types[1]
    # Try to update the workout's type to one owned by the secondary user.
    payload = postable_payload.copy()
    payload["parent_workout_type_id"] = str(secondary_user_workout_type.id)
    response = client.put(
        ROUTE, params={"id": str(wt.id)}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 404
