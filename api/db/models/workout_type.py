import uuid

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class WorkoutType(Base):
    __tablename__ = 'workout_types'

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(Text, nullable=False)
    notes: str | None = Column(Text)

    parent_workout_type_id: UUID | None = Column(UUID(as_uuid=True), ForeignKey('workout_types.id'))
    children = relationship(
        'WorkoutType',
        backref=backref('parent_workout_type', remote_side=[id])
    )