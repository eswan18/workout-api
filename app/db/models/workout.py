import uuid

from sqlalchemy import Column, ForeignKey, DateTime, Text, UUID
from sqlalchemy.orm import relationship, Mapped

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .workout_type import WorkoutType
from .user import User


class Workout(Base, ModificationTimesMixin):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    workout_type_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_types.id"), nullable=True
    )
    workout_type: Mapped[WorkoutType] = relationship("WorkoutType", backref="workouts")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship("User", backref="workouts")
