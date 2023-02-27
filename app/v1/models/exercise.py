from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.db.models import Exercise


class ExerciseIn(BaseModel):
    start_time: datetime | None
    weight: float
    weight_unit: str | None
    reps: int | None
    seconds: int | None
    notes: str | None
    # Relations
    exercise_type_id: UUID
    workout_id: UUID

    def to_orm_model(self, user_id: UUID | None) -> Exercise:
        """
        Convert to a sqlalchemy model object.
        """
        return Exercise(
            start_time=self.start_time,
            weight=self.weight,
            weight_unit=self.weight_unit,
            reps=self.reps,
            seconds=self.seconds,
            notes=self.notes,
            exercise_type_id=self.exercise_type_id,
            workout_id=self.workout_id,
            user_id=user_id,
        )

    def update_orm_model(self, model: Exercise) -> None:
        """
        Update a sqlalchemy object in-place with these values.
        """
        model.start_time = self.start_time
        model.weight = self.weight
        model.weight_unit = self.weight_unit
        model.reps = self.reps
        model.seconds = self.seconds
        model.notes = self.notes
        model.exercise_type_id = self.exercise_type_id
        model.workout_id = self.workout_id


class ExerciseInDB(ExerciseIn):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
