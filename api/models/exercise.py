from pydantic import BaseModel


class Exercise(BaseModel):
    name: str
    number_of_weights: int = 1
    notes: str


class ExerciseInDB(Exercise):
    id: str
