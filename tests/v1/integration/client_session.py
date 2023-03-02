from datetime import datetime
from functools import partial
from typing import Callable
from dataclasses import dataclass

from httpx import Response
from fastapi.testclient import TestClient

from app.v1.models.workout import WorkoutIn, WorkoutInDB
from app.v1.models.exercise import ExerciseIn, ExerciseInDB
from app.v1.models.exercise_type import ExerciseTypeInDB


@dataclass
class ClientSession:
    """
    A client that automatically passes auth.
    """

    client: TestClient
    auth: dict[str, str]

    def __getattr__(self, attr) -> Callable[..., Response]:
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

    def create_new_exercise(
        self, time: datetime, workout_id: str, ex_type_id: str
    ) -> ExerciseInDB:
        ex = ExerciseIn(
            start_time=time,
            weight=20,
            weight_unit="pounds",
            reps=8,
            workout_id=workout_id,
            exercise_type_id=ex_type_id,
        )
        response = self.post("/exercises", data=ex.json())
        assert response.status_code == 201
        (created,) = response.json()
        return ExerciseInDB.parse_obj(created)

    def create_new_ex_type(self) -> ExerciseTypeInDB:
        ...

    def get_exercises_for_workout(self, workout_id: str) -> list[ExerciseInDB]:
        response = self.get("/exercises", params={"workout_id": workout_id})
        assert response.status_code == 200
        return [ExerciseInDB.parse_obj(record) for record in response.json()]
