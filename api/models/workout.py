from datetime import datetime

from pydantic import BaseModel


class Workout(BaseModel):
    start_time: datetime
    end_time: datetime | None
    status: str
    notes: str | None
    workout_type: str | None


class WorkoutInDB(Workout):
    id: str


class WorkoutType(BaseModel):
    name: str
    notes: str
    parent_workout_type_id: str | None


class WorkoutTypeInDB(WorkoutType):
    id: str
