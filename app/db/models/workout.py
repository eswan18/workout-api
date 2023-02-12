import uuid

from sqlalchemy import Column, ForeignKey, DateTime, Text, UUID
from sqlalchemy.orm import relationship, Mapped

from ..database import Base
from .workout_type import WorkoutType
from .user import User
from .filter_mixin import FilterMixin


class Workout(Base, FilterMixin):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    status = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    workout_type_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_types.id"), nullable=True
    )
    workout_type: Mapped[WorkoutType] = relationship("WorkoutType", backref="workouts")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship("User", backref="workouts")
