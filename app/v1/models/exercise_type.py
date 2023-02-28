from uuid import UUID

from pydantic import BaseModel

from app.db.models import ExerciseType


class ExerciseTypeIn(BaseModel):
    name: str
    number_of_weights: int = 1
    notes: str | None

    def to_orm_model(self, owner_user_id: UUID | None) -> ExerciseType:
        """
        Convert to a sqlalchemy model object.
        """
        return ExerciseType(
            name=self.name,
            number_of_weights=self.number_of_weights,
            notes=self.notes,
            owner_user_id=owner_user_id,
        )

    def update_orm_model(self, model: ExerciseType) -> None:
        """
        Update a sqlalchemy object in-place with these values.
        """
        model.name = self.name
        model.number_of_weights = self.number_of_weights
        model.notes = self.notes


class ExerciseTypeInDB(ExerciseTypeIn):
    id: UUID
    owner_user_id: UUID | None

    class Config:
        orm_mode = True
