from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import WorkoutType


ROUTE = "/workout_types/"


def test_authentication_required_for_delete(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
    session_factory: sessionmaker[Session],
):
    wt_to_delete = primary_user_workout_types[0]
    params = {"id": wt_to_delete.id}

    # No auth should get a 401.
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
    with session_factory() as session:
        record = session.scalar(select(WorkoutType).filter_by(id=wt_to_delete.id))
        assert record.deleted_at == None

    # Different user auth should get a 404 because we can't find that workout type.
    response = client.delete(ROUTE, params=params, headers=secondary_test_user.auth)
    assert response.status_code == 404
    assert set(response.json().keys()) == {"detail"}
    with session_factory() as session:
        record = session.scalar(select(WorkoutType).filter_by(id=wt_to_delete.id))
        assert record.deleted_at == None


def test_cant_delete_public_workout_type(
    client: TestClient,
    public_workout_type: WorkoutType,
    session_factory: sessionmaker[Session],
):
    params = {"id": public_workout_type.id}
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
    with session_factory() as session:
        record = session.scalar(
            select(WorkoutType).filter_by(id=public_workout_type.id)
        )
        assert record.deleted_at == None


def test_can_delete_own_workout_type(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
    session_factory: sessionmaker[Session],
):
    wt_to_delete = primary_user_workout_types[0]
    params = {"id": wt_to_delete.id}

    start_time = datetime.now(tz=timezone.utc)
    response = client.delete(ROUTE, params=params, headers=primary_test_user.auth)
    end_time = datetime.now(tz=timezone.utc)
    assert response.status_code == 200
    with session_factory() as session:
        wt_to_delete = session.scalar(select(WorkoutType).filter_by(id=wt_to_delete.id))
        assert wt_to_delete.deleted_at != None
        assert start_time < wt_to_delete.deleted_at < end_time
