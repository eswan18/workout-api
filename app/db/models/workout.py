import uuid
from datetime import datetime

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime, Text, UUID
from sqlalchemy.sql.elements import ColumnElement, and_
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
    def param_filter(
        cls,
        *,
        id: uuid.UUID | None = None,
        status: str | None = None,
        workout_type_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
        min_end_time: datetime | None = None,
        max_end_time: datetime | None = None,
    ) -> ColumnElement[bool]:
        """Build a filter over user-supplied parameters"""
        f = and_(True)  # Wrapping True in `and_` helps with typing issues.
        if id is not None:
            f = and_(f, cls.id == id)
        if status is not None:
            f = and_(f, cls.status == status)
        if workout_type_id is not None:
            f = and_(cls.workout_type_id == workout_type_id)
        if user_id is not None:
            f = and_(f, cls.user_id == user_id)
        if min_start_time is not None:
            f = and_(f, cls.start_time > min_start_time)
        if max_start_time is not None:
            f = and_(f, cls.start_time < max_start_time)
        if min_end_time is not None:
            f = and_(f, cls.end_time > min_end_time)
        if max_end_time is not None:
            f = and_(f, cls.end_time < max_end_time)
        return f

    @classmethod
    def readable_by(
        cls,
        user: User,
    ) -> ColumnElement[bool]:
        """Build a filter for workouts this user can read."""
        return cls.user == user
