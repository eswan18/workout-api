from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class SetIn(BaseModel):
    start_time: datetime | None
    weight: float
    weight_unit: str | None
    reps: int | None
    seconds: int | None
    notes: str
    # Relations
    exercise_type_id: UUID
    workout_id: UUID


class SetInDB(SetIn):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
