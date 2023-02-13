import uuid

from sqlalchemy import Column, ForeignKey, Integer, Double, Text, DateTime, UUID
from sqlalchemy.orm import relationship, Mapped

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User
from .workout import Workout
from .exercise_type import ExerciseType


class Set(Base, ModificationTimesMixin):
    __tablename__ = "sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime(timezone=True))
    weight = Column(Double, nullable=False)
    weight_unit = Column(Text, nullable=True)
    reps = Column(Integer, nullable=True)
    seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    exercise_type_id = Column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id"), nullable=False
    )
    exercise_type: Mapped[ExerciseType] = relationship("ExerciseType", backref="sets")

    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False)
    workout: Mapped[Workout] = relationship("Workout", backref="sets")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship("User", backref="sets")
