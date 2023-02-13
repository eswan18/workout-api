import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Double, Text, DateTime, UUID
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
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    weight: Mapped[float] = mapped_column(Double, nullable=False)
    weight_unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Foreign keys
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id"), nullable=False
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    # Relationships
    exercise_type: Mapped[ExerciseType] = relationship("ExerciseType", backref="sets")
    workout: Mapped[Workout] = relationship("Workout", backref="sets")
    user: Mapped[User] = relationship("User", backref="sets")
