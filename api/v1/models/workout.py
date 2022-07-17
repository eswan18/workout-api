from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class Workout(BaseModel):
    start_time: datetime
    end_time: datetime | None
    status: str
    notes: str | None
    workout_type_id: UUID | None
    user_id: UUID


class WorkoutInDB(Workout):
    id: UUID

    class Config:
        orm_mode = True


class WorkoutType(BaseModel):
    name: str
    notes: str | None
    parent_workout_type_id: UUID | None


class WorkoutTypeInDB(WorkoutType):
    id: UUID

    class Config:
        orm_mode = True
