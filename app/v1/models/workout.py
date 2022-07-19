from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class WorkoutIn(BaseModel):
    start_time: datetime
    end_time: datetime | None
    status: str
    notes: str | None
    workout_type_id: UUID | None


class WorkoutInDB(WorkoutIn):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
