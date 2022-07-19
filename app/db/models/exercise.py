import uuid

from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(Text, nullable=False)
    number_of_weights: int = Column(Integer, default=1, nullable=False)
    notes: str | None = Column(Text)
