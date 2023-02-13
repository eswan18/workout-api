import uuid

from sqlalchemy import ForeignKey, Integer, Double, Text, DateTime, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User
from .workout import Workout
from .exercise_type import ExerciseType


class Set(Base, ModificationTimesMixin):
    __tablename__ = "sets"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = mapped_column(DateTime(timezone=True))
    weight = mapped_column(Double, nullable=False)
    weight_unit = mapped_column(Text, nullable=True)
    reps = mapped_column(Integer, nullable=True)
    seconds = mapped_column(Integer, nullable=True)
    notes = mapped_column(Text, nullable=True)
    # Foreign keys
    exercise_type_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id"), nullable=False
    )
    workout_id = mapped_column(UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # Relationships
    exercise_type: Mapped[ExerciseType] = relationship("ExerciseType", backref="sets")
    workout: Mapped[Workout] = relationship("Workout", backref="sets")
    user: Mapped[User] = relationship("User", backref="sets")
