from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.db.models import Workout


class WorkoutIn(BaseModel):
    start_time: datetime | None
    end_time: datetime | None
    status: str
    notes: str | None
    workout_type_id: UUID | None

    def to_orm_model(self, user_id: UUID) -> Workout:
        """
        Convert to a sqlalchemy model object.
        """
        return Workout(
            start_time=self.start_time,
            end_time=self.end_time,
            status=self.status,
            notes=self.notes,
            workout_type_id=self.workout_type_id,
        )

    def update_orm_model(self, model: Workout) -> None:
        """
        Update a sqlalchemy object in-place with these values.
        """
        model.start_time = self.start_time
        model.end_time = self.end_time
        model.status = self.status
        model.notes = self.notes
        model.workout_type_id = self.workout_type_id


class WorkoutInDB(WorkoutIn):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
