import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from ..database import Base
from .user import User


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    number_of_weights = Column(Integer, default=1, nullable=False)
    notes = Column(Text, nullable=True)

    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user: Mapped[User] = relationship(User, backref="owned_exercises")
