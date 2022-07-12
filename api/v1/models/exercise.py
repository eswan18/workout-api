from uuid import UUID

from pydantic import BaseModel


class Exercise(BaseModel):
    name: str
    number_of_weights: int = 1
    notes: str | None


class ExerciseInDB(Exercise):
    id: UUID

    class Config:
        orm_mode = True
