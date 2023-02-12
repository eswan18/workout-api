import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from ..database import Base
from .user import User
from .workout import Workout
from .exercise import Exercise


class Set(Base):
    __tablename__ = "sets"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time: datetime = Column(DateTime, nullable=False)
    weight: float = Column(Float, nullable=False)
    weight_unit: str | None = Column(Text)
    reps: int | None = Column(Integer)
    seconds: int | None = Column(Integer)
    notes: str | None = Column(Text)

    exercise_id: UUID = Column(
        UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False
    )
    exercise: Mapped[Exercise] = relationship("Exercise", backref="sets")

    workout_id: UUID = Column(
        UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False
    )
    workout: Mapped[Workout] = relationship("Workout", backref="sets")

    user_id: UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship("User", backref="sets")
