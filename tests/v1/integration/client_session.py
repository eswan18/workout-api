from datetime import datetime
from functools import partial
from dataclasses import dataclass
from typing import Callable

from fastapi.testclient import TestClient

from app.v1.models.workout import WorkoutIn, WorkoutInDB
from app.v1.models.exercise import ExerciseInDB
from app.v1.models.exercise_type import ExerciseTypeInDB


@dataclass
class ClientSession:
    """
    A client that automatically passes auth.
    """

    client: TestClient
    auth: dict[str, str]

    def __getattr__(self, attr) -> Callable:
        if attr in ("get", "post", "put", "patch", "delete"):
            client_method = getattr(self.client, attr)
            return partial(client_method, headers=self.auth)
        else:
            raise super().__getattr__(self, attr)

    def start_new_workout(self, time: datetime) -> WorkoutInDB:
        wkt = WorkoutIn(
            start_time=time,
            end_time=None,
            status="started",
            workout_type_id=None,  # We are an independent thinker
        )
        response = self.post("/workouts", data=wkt.json())
        assert response.status_code == 201
        (created,) = response.json()
        return WorkoutInDB.parse_obj(created)

    def create_new_exercise(self, workout_id: str) -> ExerciseInDB:
        ...

    def create_new_ex_type(self) -> ExerciseTypeInDB:
        ...

    def get_exercises_for_workout(self, workout_id: str) -> list[ExerciseInDB]:
        ...
