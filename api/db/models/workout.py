import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base
from .workout_type import WorkoutType
from .user import User


class Workout(Base):
    __tablename__ = "workouts"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time: datetime | None = Column(DateTime)
    end_time: datetime | None = Column(DateTime)
    status: str = Column(Text, nullable=False)
    notes: str | None = Column(Text)

    workout_type_id: UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("workout_types.id")
    )
    workout_type: WorkoutType = relationship("WorkoutType", backref="workouts")

    user_id: UUID = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user: User = relationship("User", backref="workouts")
