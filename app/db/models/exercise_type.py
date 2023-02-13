import uuid

from sqlalchemy import ForeignKey, Integer, Text, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User


class ExerciseType(Base, ModificationTimesMixin):
    __tablename__ = "exercise_types"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(Text, nullable=False)
    number_of_weights = mapped_column(Integer, default=1, nullable=False)
    notes = mapped_column(Text, nullable=True)
    # Foreign keys
    owner_user_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    # Relationships
    owner: Mapped[User] = relationship(User, backref="owned_exercises")
