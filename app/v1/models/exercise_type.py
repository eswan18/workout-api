from uuid import UUID

from pydantic import BaseModel


class ExerciseTypeIn(BaseModel):
    name: str
    number_of_weights: int = 1
    notes: str | None


class ExerciseTypeInDB(ExerciseTypeIn):
    id: UUID
    owner_user_id: UUID | None

    class Config:
        orm_mode = True
