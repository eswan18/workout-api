from typing import Self
import uuid
from datetime import datetime

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, Double, Text, DateTime, UUID
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User
from .workout import Workout
from .exercise_type import ExerciseType


class Set(Base, ModificationTimesMixin):
    __tablename__ = "sets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    weight: Mapped[float] = mapped_column(Double)
    weight_unit: Mapped[str | None] = mapped_column(Text)
    reps: Mapped[int | None] = mapped_column(Integer)
    seconds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    # Foreign keys
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id")
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workouts.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    # Relationships
    exercise_type: Mapped[ExerciseType] = relationship("ExerciseType", backref="sets")
    workout: Mapped[Workout] = relationship("Workout", backref="sets")
    user: Mapped[User] = relationship("User", backref="sets")

    @classmethod
    def apply_params(
        cls,
        query: Select[tuple[Self]],
        *,
        id: uuid.UUID | None = None,
        exercise_type_id: uuid.UUID | None = None,
        workout_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
    ) -> Select[tuple[Self]]:
        if id is not None:
            query = query.where(cls.id == id)
        if exercise_type_id is not None:
            query = query.where(cls.exercise_type_id == exercise_type_id)
        if workout_id is not None:
            query = query.where(cls.workout_id == workout_id)
        if user_id is not None:
            query = query.where(cls.user_id == user_id)
        if min_start_time is not None:
            query = query.where(cls.start_time > min_start_time)
        if max_start_time is not None:
            query = query.where(cls.start_time < max_start_time)
        return query

    @classmethod
    def apply_read_permissions(
        cls,
        query: Select[tuple[Self]],
        user: User,
    ) -> Select[tuple[Self]]:
        """
        Limit a query down to only the resources a user has access to read.
        """
        return query.where(cls.user == user)
