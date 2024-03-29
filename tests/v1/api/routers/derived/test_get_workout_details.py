from uuid import uuid4

from fastapi.testclient import TestClient
from app.db.models.user import UserWithAuth
from app.db.models import Workout, ExerciseType, Exercise


ROUTE = "/derived/workout_details/"


def test_unauthenticated_user_cant_read(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    primary_user_exercises: tuple[Exercise, ...],
):
    workout, exercise_type = primary_user_workout_and_exercise_type
    # Try with no creds.
    response = client.get(ROUTE, params={"id": workout.id})
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401
    assert set(response.json().keys()) == {"detail"}

    # Try with bad creds.
    bad_user_auth = primary_test_user.auth.copy()
    bad_user_auth.update(Authorization="Bearer 123abc")
    response = client.get(ROUTE, params={"id": workout.id}, headers=bad_user_auth)
    # Make sure we get a 401 and no data comes back.
    assert response.status_code == 401


def test_user_cant_read_others_workouts(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    primary_user_exercises: tuple[Exercise, ...],
):
    workout, exercise_type = primary_user_workout_and_exercise_type
    response = client.get(
        ROUTE, params={"id": workout.id}, headers=secondary_test_user.auth
    )
    assert response.status_code == 404


def test_invalid_id_returns_404(client: TestClient, primary_test_user: UserWithAuth):
    imaginary_id = uuid4()
    response = client.get(
        ROUTE, params={"id": imaginary_id}, headers=primary_test_user.auth
    )
    assert response.status_code == 404


def test_returns_correct_workout_details(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    primary_user_exercises: tuple[Exercise, ...],
):
    workout, exercise_type = primary_user_workout_and_exercise_type
    exercises = primary_user_exercises

    # Fetch the workout details
    response = client.get(
        ROUTE, params={"id": workout.id}, headers=primary_test_user.auth
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    payload_item = payload[0]
    assert payload_item.keys() == {"workout", "exercises"}
    payload_workout = payload_item["workout"]
    assert payload_workout["id"] == str(workout.id)

    # Make sure the workout type was included if it exists.
    if workout.workout_type_id is None:
        assert payload_workout["workout_type_id"] is None
        assert payload_workout["workout_type_name"] is None
    else:
        assert payload_workout["workout_type_id"] == str(workout.workout_type_id)
        assert payload_workout["workout_type_name"] == workout.workout_type.name

    payload_exercises = payload_item["exercises"]
    assert len(payload_exercises) == len(exercises)
    # Make sure the exercise types are included.
    for payload_exercise in payload_exercises:
        assert payload_exercise["exercise_type_id"] == str(exercise_type.id)
        assert payload_exercise["exercise_type_name"] == exercise_type.name


def test_returns_correct_workout_details_when_there_are_no_exercises(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
):
    workout, exercise_type = primary_user_workout_and_exercise_type
    # Fetch the workout details
    response = client.get(
        ROUTE, params={"id": workout.id}, headers=primary_test_user.auth
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    payload_item = payload[0]
    assert payload_item.keys() == {"workout", "exercises"}
    payload_workout = payload_item["workout"]
    assert payload_workout["id"] == str(workout.id)
    # Make sure there are no exercises included.
    assert len(payload_item["exercises"]) == 0


def test_without_id_still_doesnt_let_user_read_others_workouts(
    client: TestClient,
    secondary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    primary_user_exercises: tuple[Exercise, ...],
):
    response = client.get(ROUTE, headers=secondary_test_user.auth)
    # We should receive a "successful" response but not get any data back, since we didn't ask for a specific workout.
    assert response.status_code == 200
    assert response.json() == []


def test_without_id_returns_all_workout_details(
    client: TestClient,
    primary_test_user: UserWithAuth,
    primary_user_workout_and_exercise_type: tuple[Workout, ExerciseType],
    primary_user_exercises: tuple[Exercise, ...],
    primary_user_exercise_of_different_type_and_workout: tuple[
        Workout, ExerciseType, Exercise
    ],
):
    workout, _ = primary_user_workout_and_exercise_type
    exercises = primary_user_exercises
    (
        other_workout,
        _,
        other_exercise,
    ) = primary_user_exercise_of_different_type_and_workout

    # Fetch the workout details
    response = client.get(ROUTE, headers=primary_test_user.auth)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    # Make sure each one has the correct workout ID and exercises.
    payload_wkt_id = {item["workout"]["id"] for item in payload}
    assert payload_wkt_id == {str(workout.id), str(other_workout.id)}
    main_exercises_ids = {str(exercise.id) for exercise in exercises}
    other_exercise_id = str(other_exercise.id)
    for item in payload:
        if item["workout"]["id"] == str(workout.id):
            assert {
                str(exercise["id"]) for exercise in item["exercises"]
            } == main_exercises_ids
        else:
            assert {str(exercise["id"]) for exercise in item["exercises"]} == {
                other_exercise_id
            }
