import uuid

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref, Mapped

from ..database import Base
from .user import User


class WorkoutType(Base):
    __tablename__ = "workout_types"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(Text, nullable=False)
    notes: str | None = Column(Text)

    parent_workout_type_id: UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("workout_types.id")
    )
    children: list["WorkoutType"] = relationship(
        "WorkoutType", backref=backref("parent_workout_type", remote_side=[id])
    )

    owner_user_id: UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    user: Mapped[User] = relationship(User, backref="owned_workout_types")
