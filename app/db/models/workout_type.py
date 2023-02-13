import uuid

from sqlalchemy import ForeignKey, Text, UUID
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User


class WorkoutType(Base, ModificationTimesMixin):
    __tablename__ = "workout_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Foreign keys
    parent_workout_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_types.id"), nullable=True
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    # Relationships
    children: Mapped[list["WorkoutType"]] = relationship(
        "WorkoutType", backref=backref("parent_workout_type", remote_side=[id])
    )
    owner: Mapped[User] = relationship(User, backref="owned_workout_types")
