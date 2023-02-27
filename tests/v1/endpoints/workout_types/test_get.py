from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.sql import select, delete
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.user import UserWithAuth
from app.db import WorkoutType


ROUTE = "/workout_types/"


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    # Try with no creds.
    response = client.get(ROUTE)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}

    # Try with bad creds.
    bad_user_auth = primary_test_user.auth.copy()
    bad_user_auth.update(Authorization="Bearer 123abc")
    response = client.get(ROUTE, headers=bad_user_auth)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}


def test_one_user_cant_read_anothers_workout_types(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    response = client.get(ROUTE, headers=secondary_test_user.auth)
    assert response.status_code == 200
    # Make sure we only get public workout types.
    workout_types = response.json()
    for workout_type in workout_types:
        assert workout_type["owner_user_id"] == None


def test_user_can_read_own_and_public_workout_types(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
    primary_user_soft_deleted_workout_type: WorkoutType,
    session_factory: sessionmaker[Session],
):
    """
    Users can read their own and public workout types but not soft deleted ones.
    """
    # How many public workouts should there be?
    with session_factory() as session:
        n_public_workout_types = session.scalar(
            select(count(WorkoutType.id)).where(WorkoutType.owner_user_id == None)
        )
    # How many private workouts should there be?
    n_private_workout_types = len(primary_user_workout_types)

    response = client.get(ROUTE, headers=primary_test_user.auth)
    assert response.status_code == 200
    workout_types = response.json()
    assert len(workout_types) == (n_public_workout_types + n_private_workout_types)
    for workout_type in workout_types:
        assert workout_type["owner_user_id"] in (None, str(primary_test_user.user.id))


def test_user_can_read_newly_written_workout_type(
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
            delete(WorkoutType).where(WorkoutType.id == UUID(payload[0]["id"]))
        )
        session.commit()
        assert result.rowcount == 1


def test_filtering(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_types: tuple[WorkoutType, ...],
):
    # Get by ID.
    params = {"id": primary_user_workout_types[0].id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == primary_user_workout_types[0].name

    # Get by name.
    params = {"name": primary_user_workout_types[1].name}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == str(primary_user_workout_types[1].id)

    # Get by parent ID.
    params = {"owner_user_id": primary_user_workout_types[1].owner_user_id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == len(primary_user_workout_types)
