from uuid import UUID

from pydantic import BaseModel


class ExerciseIn(BaseModel):
    name: str
    number_of_weights: int = 1
    notes: str | None


class ExerciseInDB(ExerciseIn):
    id: UUID
    owner_user_id: UUID | None

    class Config:
        orm_mode = True
