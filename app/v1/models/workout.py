from uuid import UUID
from datetime import datetime
from typing import Literal, TypeAlias

from pydantic import BaseModel

from app.db.models import Workout


# Unfortunately these values are duplicated since we can't pass type hints at runtime.
valid_status_values = ["in-progress", "paused", "completed"]
StatusValue: TypeAlias = Literal["in-progress", "paused", "completed"]


class WorkoutIn(BaseModel):
    start_time: datetime | None
    end_time: datetime | None
    status: StatusValue
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
            user_id=user_id,
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
