from fastapi.testclient import TestClient

from app.db.models.user import UserWithAuth
from app.db import Exercise, Workout, ExerciseType


ROUTE = "/exercises/"


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
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


def test_user_cant_read_others_exercises(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
):
    response = client.get(ROUTE, headers=secondary_test_user.auth)
    assert response.status_code == 200
    # This user owns zero exercises.
    workouts = response.json()
    assert len(workouts) == 0


def test_user_can_read_own_exercises(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
    primary_user_soft_deleted_exercise: Exercise,
):
    """
    Users can read their own workouts but not soft deleted ones.
    """
    response = client.get(ROUTE, headers=primary_test_user.auth)
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) == len(primary_user_exercises)
    for exercise in exercises:
        assert exercise["user_id"] == str(primary_test_user.user.id)


def test_filtering(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_exercises: tuple[Exercise, ...],
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    primary_user_exercise_of_different_type_and_workout,
):
    wkt, ex_tp = primary_user_workout_and_exercise_type
    # Get by ID.
    params = {"id": primary_user_exercises[0].id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1

    # Get by workout.
    params = {"workout_id": str(wkt.id)}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == len(primary_user_exercises)
    for exercise in payload:
        assert exercise["workout_id"] == str(wkt.id)

    # Get by exercise type.
    params = {"exercise_type_id": ex_tp.id}
    response = client.get(ROUTE, params=params, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == len(primary_user_exercises)
    for exercise in payload:
        assert exercise["exercise_type_id"] == str(ex_tp.id)
