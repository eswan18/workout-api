import uuid

from sqlalchemy import Column, ForeignKey, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Set(Base):
    __tablename__ = 'sets'

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    weight: float = Column(Float, nullable=False)
    weight_unit: str | None = Column(Text)
    reps: int | None = Column(Integer)
    seconds: int | None = Column(Integer)
    notes: str | None = Column(Text)

    exercise_id: UUID = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    exercise = relationship("Exercise", backref="sets")

    workout_id: UUID = Column(UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False)
    workout = relationship("Workout", backref="sets")
