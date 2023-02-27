from uuid import UUID

from pydantic import BaseModel

from app.db.models import WorkoutType


class WorkoutTypeIn(BaseModel):
    name: str
    notes: str | None
    parent_workout_type_id: UUID | None

    def to_orm_model(self, owner_user_id: UUID | None) -> WorkoutType:
        """
        Convert to a sqlalchemy model object.
        """
        return WorkoutType(
            name=self.name,
            notes=self.notes,
            parent_workout_type_id=self.parent_workout_type_id,
            owner_user_id=owner_user_id,
        )

    def update_orm_model(self, model: WorkoutType) -> None:
        """
        Update a sqlalchemy object in-place with these values.
        """
        model.name = self.name
        model.notes = self.notes
        model.parent_workout_type_id = self.parent_workout_type_id


class WorkoutTypeInDB(WorkoutTypeIn):
    id: UUID
    owner_user_id: UUID | None

    class Config:
        orm_mode = True
