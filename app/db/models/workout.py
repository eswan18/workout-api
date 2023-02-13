import uuid

from sqlalchemy import ForeignKey, DateTime, Text, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .workout_type import WorkoutType
from .user import User


class Workout(Base, ModificationTimesMixin):
    __tablename__ = "workouts"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = mapped_column(DateTime(timezone=True), nullable=True)
    end_time = mapped_column(DateTime(timezone=True), nullable=True)
    status = mapped_column(Text, nullable=False)
    notes = mapped_column(Text, nullable=True)
    # Foreign keys
    workout_type_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_types.id"), nullable=True
    )
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # Relationships
    workout_type: Mapped[WorkoutType] = relationship("WorkoutType", backref="workouts")
    user: Mapped[User] = relationship("User", backref="workouts")
