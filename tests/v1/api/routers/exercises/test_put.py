from uuid import UUID
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import Exercise, Workout, ExerciseType


ROUTE = "/exercises"


def test_unauthenticated_user_cant_update(
    client: TestClient,
    postable_payload: dict[str, str],
    primary_user_exercises: tuple[Exercise, ...],
):
    ex = primary_user_exercises[0]
    # No creds
    response = client.put(ROUTE, params={"id": ex.id}, json=postable_payload)
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
    primary_user_exercises: tuple[Exercise, ...],
    session_factory: sessionmaker[Session],
):
    ex = primary_user_exercises[0]
    response = client.put(
        ROUTE,
        params={"id": ex.id},
        json=postable_payload,
        headers=primary_test_user.auth,
    )
    assert response.status_code == 200
    # Make sure the record has been changed in the db.
    with session_factory() as session:
        query = select(Exercise).where(Exercise.id == ex.id)
        record = session.execute(query).scalar()
        assert record.id == ex.id
        assert record.start_time == datetime.fromisoformat(
            postable_payload["start_time"]
        )
        assert record.reps == postable_payload["reps"]
        assert record.workout_id == UUID(postable_payload["workout_id"])
        assert record.exercise_type_id == UUID(postable_payload["exercise_type_id"])
        assert record.user_id == primary_test_user.user.id
        # Hacky way to confirm that the updated_at field was changed.
        assert record.updated_at > record.created_at


def test_partial_payload_is_rejected(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
    primary_user_exercises: tuple[Exercise, ...],
):
    """
    Omitting a mandatory field of a exercise results in a 401.

    Mandatory fields are workout_id & exercise_id.
    """
    ex = primary_user_exercises[0]
    payload = {"start_time": postable_payload["start_time"]}
    response = client.put(
        ROUTE, params={"id": str(ex.id)}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 422
    with session_factory() as session:
        # Confirm that the record wasn't modified.
        query = select(Exercise).where(Exercise.id == ex.id)
        record = session.execute(query).scalars().one()
        assert record.start_time == ex.start_time


@pytest.mark.xfail(reason="This check isn't implemented yet")
def test_user_cant_set_workout_to_one_that_isnt_theirs(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
    secondary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    postable_payload: dict[str, str],
):
    """
    Users can't update an exercise to set its workout ID to a workout that isn't theirs.
    """
    # Get an exercise owned by the primary user.
    ex = primary_user_exercises[0]
    # Try to update the exercise's workout to one that is owned by the secondary user.
    payload = postable_payload.copy()
    payload["workout_id"] = str(secondary_user_workout_and_exercise_type[0].id)
    response = client.put(ROUTE, params={"id": str(ex.id)}, json=payload, headers=primary_test_user.auth)
    assert response.status_code == 400


@pytest.mark.xfail(reason="This check isn't implemented yet")
def test_user_cant_set_workout_to_one_that_isnt_theirs(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
    secondary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    postable_payload: dict[str, str],
):
    """
    Users can't update an exercise to set its exercise type to one that isn't theirs.
    """
    # Get an exercise owned by the primary user.
    ex = primary_user_exercises[0]
    # Try to update the exercise's workout to one that is owned by the secondary user.
    payload = postable_payload.copy()
    payload["exercise_type_id"] = str(secondary_user_workout_and_exercise_type[1].id)
    response = client.put(ROUTE, params={"id": str(ex.id)}, json=payload, headers=primary_test_user.auth)
    assert response.status_code == 400