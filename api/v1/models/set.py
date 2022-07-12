from uuid import UUID

from pydantic import BaseModel


class Set(BaseModel):
    weight: float
    weight_unit: str | None
    reps: int | None
    seconds: int | None
    notes: str
    # Relations
    exercise_id: UUID
    workout_id: UUID
    user_id: UUID


class SetInDB(Set):
    id: UUID

    class Config:
        orm_mode = True
