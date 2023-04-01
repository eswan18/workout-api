from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import select

from app.db.models.user import UserWithAuth
from app.db import Workout, WorkoutType


ROUTE = "/workouts"


def test_unauthenticated_user_cant_update(
    client: TestClient,
    postable_payload: dict[str, str],
    primary_user_workouts: tuple[Workout, ...],
):
    wkt1 = primary_user_workouts[0]
    # No creds
    response = client.put(ROUTE, params={"id": wkt1.id}, json=postable_payload)
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
    primary_user_workouts: tuple[Workout, ...],
    session_factory: sessionmaker[Session],
):
    wkt1 = primary_user_workouts[0]
    response = client.put(
        ROUTE,
        params={"id": wkt1.id},
        json=postable_payload,
        headers=primary_test_user.auth,
    )
    assert response.status_code == 200
    # Make sure the record has been changed in the db.
    with session_factory() as session:
        query = select(Workout).where(Workout.id == wkt1.id)
        record = session.execute(query).scalar()
        assert record.id == wkt1.id
        assert record.start_time == datetime.fromisoformat(
            postable_payload["start_time"] + "+00:00",
        )
        assert record.end_time == postable_payload["end_time"]
        assert record.status == postable_payload["status"]
        assert record.workout_type_id == postable_payload["workout_type_id"]
        assert record.user_id == primary_test_user.user.id
        # Hacky way to confirm that the updated_at field was changed.
        assert record.updated_at > record.created_at


def test_partial_payload_is_rejected(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
    primary_user_workouts: tuple[Workout, ...],
):
    """
    Omitting the mandatory field (status) of a workout results in a 401.
    """
    wkt1 = primary_user_workouts[0]
    wkt1_id, wkt1_start_time = wkt1.id, wkt1.start_time
    payload = {"start_time": postable_payload["start_time"]}
    response = client.put(
        ROUTE, params={"id": wkt1_id}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 422
    with session_factory() as session:
        # Confirm that the record wasn't modified.
        query = select(Workout).where(Workout.id == wkt1.id)
        record = session.execute(query).scalars().one()
        assert record.start_time == wkt1_start_time


def test_user_can_set_workout_type_to_public_one(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workouts: tuple[Workout, ...],
    public_workout_type: WorkoutType,
    postable_payload: dict[str, str],
):
    """
    Users can update a workout to set its type to a public one.

    Since we have a test that setting a workout type to one owned by another user isn't
    allowed, this test is a good check to be sure we're not disallowing public workout
    types as well.
    """
    # Get a workout owned by the primary user.
    wkt = primary_user_workouts[0]
    # Try to update the workout's type to one owned by the secondary user.
    payload = postable_payload.copy()
    payload["workout_type_id"] = str(public_workout_type.id)
    response = client.put(
        ROUTE, params={"id": str(wkt.id)}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 200


def test_user_cant_set_workout_type_to_one_owned_by_another_user(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workouts: tuple[Workout, ...],
    secondary_user_workout_type: WorkoutType,
    postable_payload: dict[str, str],
):
    """Users can't update a workout to set its type to one owned by another user."""
    # Get a workout owned by the primary user.
    wkt = primary_user_workouts[0]
    # Try to update the workout's type to one owned by the secondary user.
    payload = postable_payload.copy()
    payload["workout_type_id"] = str(secondary_user_workout_type.id)
    response = client.put(
        ROUTE, params={"id": str(wkt.id)}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 404
