import uuid

from sqlalchemy import Column, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship, backref, Mapped

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User


class WorkoutType(Base, ModificationTimesMixin):
    __tablename__ = "workout_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    parent_workout_type_id = Column(
        UUID(as_uuid=True), ForeignKey("workout_types.id"), nullable=True
    )
    children: Mapped[list["WorkoutType"]] = relationship(
        "WorkoutType", backref=backref("parent_workout_type", remote_side=[id])
    )

    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    owner: Mapped[User] = relationship(User, backref="owned_workout_types")
