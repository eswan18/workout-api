from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import select
from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth
from app.db import ExerciseType

ROUTE = "/exercise_types/"


def test_unauthenticated_user_cant_update(
    client: TestClient,
    postable_payload: dict[str, str],
    primary_user_exercise_types: tuple[ExerciseType, ...],
):
    ex = primary_user_exercise_types[0]
    # No creds
    response = client.patch(ROUTE, params={"id": ex.id}, json=postable_payload)
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
    primary_user_exercise_types: tuple[ExerciseType, ...],
    session_factory: sessionmaker[Session],
):
    ex = primary_user_exercise_types[0]
    response = client.patch(
        ROUTE,
        params={"id": ex.id},
        json=postable_payload,
        headers=primary_test_user.auth,
    )

    with session_factory() as session:
        query = select(ExerciseType).where(ExerciseType.id == ex.id)
        record = session.execute(query).scalar()
        assert record.id == ex.id
    assert response.status_code == 200
    # Make sure the record has been changed in the db.
    with session_factory() as session:
        query = select(ExerciseType).where(ExerciseType.id == ex.id)
        record = session.execute(query).scalar()
        assert record.id == ex.id
        assert record.name == postable_payload["name"]
        assert record.owner_user_id == primary_test_user.user.id
        assert record.notes is not None
        # Hacky way to confirm that the updated_at field was changed.
        assert record.updated_at > record.created_at


def test_empty_payload_is_accepted(
    client: TestClient,
    primary_test_user: UserWithAuth,
    session_factory: sessionmaker[Session],
    primary_user_exercise_types: tuple[ExerciseType, ...],
):
    """
    Omitting a fields of an exercise type is allowed but does nothing.
    """
    ex_id = primary_user_exercise_types[0].id
    payload = {}
    response = client.patch(
        ROUTE, params={"id": ex_id}, json=payload, headers=primary_test_user.auth
    )
    assert response.status_code == 200
    with session_factory() as session:
        # Confirm that the record wasn't modified.
        query = select(ExerciseType).where(ExerciseType.id == ex_id)
        record = session.execute(query).scalars().one()
        assert record.id == ex_id
        assert record.name is not None
