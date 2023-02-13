import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text, UUID
from sqlalchemy.orm import relationship, Mapped

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User


class Exercise(Base, ModificationTimesMixin):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    number_of_weights = Column(Integer, default=1, nullable=False)
    notes = Column(Text, nullable=True)

    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    owner: Mapped[User] = relationship(User, backref="owned_exercises")
