from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import ExerciseType


ROUTE = "/exercise_types/"


def test_authentication_required_for_delete(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_exercise_types: tuple[ExerciseType, ...],
    session_factory: sessionmaker[Session],
):
    wt_to_delete = primary_user_exercise_types[0]
    params = {"id": wt_to_delete.id}

    # No auth should get a 401.
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
    with session_factory() as session:
        record = session.scalar(select(ExerciseType).filter_by(id=wt_to_delete.id))
        assert record.deleted_at == None

    # Different user auth should get a 404 because we can't find that workout type.
    response = client.delete(ROUTE, params=params, headers=secondary_test_user.auth)
    assert response.status_code == 404
    assert set(response.json().keys()) == {"detail"}
    with session_factory() as session:
        record = session.scalar(select(ExerciseType).filter_by(id=wt_to_delete.id))
        assert record.deleted_at == None


def test_cant_delete_public_exercise_type(
    client: TestClient,
    public_exercise_type: ExerciseType,
    session_factory: sessionmaker[Session],
):
    params = {"id": public_exercise_type.id}
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}
    with session_factory() as session:
        record = session.scalar(select(ExerciseType).filter_by(id=ExerciseType.id))
        assert record.deleted_at == None


def test_can_delete_own_workout_type(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercise_types: tuple[ExerciseType, ...],
    session_factory: sessionmaker[Session],
):
    wt_to_delete = primary_user_exercise_types[0]
    params = {"id": wt_to_delete.id}

    start_time = datetime.now(tz=timezone.utc)
    response = client.delete(ROUTE, params=params, headers=primary_test_user.auth)
    end_time = datetime.now(tz=timezone.utc)
    assert response.status_code == 200
    with session_factory() as session:
        record = session.scalar(select(ExerciseType).filter_by(id=wt_to_delete.id))
        assert record.deleted_at != None
        assert start_time < record.deleted_at < end_time
