from uuid import UUID

from pydantic import BaseModel


class WorkoutTypeIn(BaseModel):
    name: str
    notes: str | None
    parent_workout_type_id: UUID | None


class WorkoutTypeInDB(WorkoutTypeIn):
    id: UUID

    class Config:
        orm_mode = True
