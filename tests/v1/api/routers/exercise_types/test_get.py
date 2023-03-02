from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.sql import select, delete
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import ExerciseType


ROUTE = "/exercise_types/"


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercise_types: tuple[ExerciseType, ...],
):
    # Try with no creds.
    response = client.get(ROUTE)
    assert response.status_code == 401

    # Try with bad creds.
    bad_user_auth = primary_test_user.auth.copy()
    bad_user_auth.update(Authorization="Bearer 123abc")
    response = client.get(ROUTE, headers=bad_user_auth)
    assert response.status_code == 401


def test_one_user_cant_read_anothers_exercise_types(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_exercise_types: tuple[ExerciseType, ...],
):
    response = client.get(ROUTE, headers=secondary_test_user.auth)
    assert response.status_code == 200
    # Make sure we only get public workout types.
    ex_types = response.json()
    for ex_tp in ex_types:
        assert ex_tp["owner_user_id"] == None


def test_user_can_read_own_and_public_exercise_types(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercise_types: tuple[ExerciseType, ...],
    primary_user_soft_deleted_exercise_type: ExerciseType,
    session_factory: sessionmaker[Session],
):
    """
    Users can read their own and public exercise types but not soft deleted ones.
    """
    # How many public exercise types should there be?
    with session_factory() as session:
        n_public_ex_tps = session.scalar(
            select(count(ExerciseType.id)).where(ExerciseType.owner_user_id == None)
        )
    # How many private exercise types should there be?
    n_private_ex_tps = len(primary_user_exercise_types)

    response = client.get(ROUTE, headers=primary_test_user.auth)
    assert response.status_code == 200
    exercise_types = response.json()
    assert len(exercise_types) == (n_public_ex_tps + n_private_ex_tps)
    for ex_tp in exercise_types:
        assert ex_tp["owner_user_id"] in (None, str(primary_test_user.user.id))


def test_user_can_read_newly_written_exercise_type(
    client: TestClient,
    primary_test_user: UserWithAuth,
    postable_payload: dict[str, str],
    session_factory: sessionmaker[Session],
):
    response = client.post(ROUTE, json=postable_payload, headers=primary_test_user.auth)
    id = response.json()[0]["id"]
    params = {"id": id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == id

    # Clean up and make sure that record was in the db.
    with session_factory() as session:
        result = session.execute(
            delete(ExerciseType).where(ExerciseType.id == UUID(payload[0]["id"]))
        )
        session.commit()
        assert result.rowcount == 1


def test_filtering(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercise_types: tuple[ExerciseType, ...],
):
    # Get by ID.
    params = {"id": primary_user_exercise_types[0].id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == primary_user_exercise_types[0].name

    # Get by name.
    params = {"name": primary_user_exercise_types[1].name}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == str(primary_user_exercise_types[1].id)
