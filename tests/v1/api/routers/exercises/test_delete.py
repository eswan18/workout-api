from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import select

from app.db.models.user import UserWithAuth
from app.db import Exercise


ROUTE = "/exercises/"


def test_authentication_required_for_delete(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
    session_factory: sessionmaker[Session],
):
    ex_to_delete = primary_user_exercises[0]
    params = {"id": ex_to_delete.id}

    # No auth should get a 401.
    response = client.delete(ROUTE, params=params)
    assert response.status_code == 401
    with session_factory() as session:
        record = session.scalar(select(Exercise).filter_by(id=ex_to_delete.id))
        assert record.deleted_at == None

    # Different user auth should get a 404 because we can't find that workout type.
    response = client.delete(ROUTE, params=params, headers=secondary_test_user.auth)
    assert response.status_code == 404
    with session_factory() as session:
        record = session.scalar(select(Exercise).filter_by(id=ex_to_delete.id))
        assert record.deleted_at == None


def test_can_delete_own_exercise(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
    session_factory: sessionmaker[Session],
):
    ex_to_delete = primary_user_exercises[0]
    params = {"id": ex_to_delete.id}

    start_time = datetime.now(tz=timezone.utc)
    response = client.delete(ROUTE, params=params, headers=primary_test_user.auth)
    end_time = datetime.now(tz=timezone.utc)
    assert response.status_code == 200
    with session_factory() as session:
        record = session.scalar(select(Exercise).filter_by(id=ex_to_delete.id))
        assert record.deleted_at != None
        assert start_time < record.deleted_at < end_time
