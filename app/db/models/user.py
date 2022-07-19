import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: str = Column(Text, unique=True, nullable=False)
    pw_hash: str = Column(Text, nullable=False)