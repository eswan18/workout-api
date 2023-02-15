from typing import Self
import uuid
from datetime import datetime

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime, Text, UUID
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .workout_type import WorkoutType
from .user import User


class Workout(Base, ModificationTimesMixin):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    # Foreign keys
    workout_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_types.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    # Relationships
    workout_type: Mapped[WorkoutType] = relationship("WorkoutType", backref="workouts")
    user: Mapped[User] = relationship("User", backref="workouts")

    @classmethod
    def apply_params(
        cls,
        query: Select[tuple[Self]],
        *,
        id: uuid.UUID | None = None,
        status: str | None = None,
        workout_type_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
        min_end_time: datetime | None = None,
        max_end_time: datetime | None = None,
    ) -> Select[tuple[Self]]:
        if id is not None:
            query = query.where(cls.id == id)
        if status is not None:
            query = query.where(cls.status == status)
        if workout_type_id is not None:
            query = query.where(cls.workout_type_id == workout_type_id)
        if user_id is not None:
            query = query.where(cls.user_id == user_id)
        if min_start_time is not None:
            query = query.where(cls.start_time > min_start_time)
        if max_start_time is not None:
            query = query.where(cls.start_time < max_start_time)
        if min_end_time is not None:
            query = query.where(cls.end_time > min_end_time)
        if max_end_time is not None:
            query = query.where(cls.end_time < max_end_time)
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
