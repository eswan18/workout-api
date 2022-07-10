from pydantic import BaseModel


class Set(BaseModel):
    weight: float
    weight_unit: str = 'lbs'
    reps: int | None
    seconds: int | None
    notes: str
    # Relations
    exercise_id: str
    workout_id: str


class SetInDB(Set):
    id: str
