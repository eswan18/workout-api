import uuid

from sqlalchemy import Column, Text, UUID

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin


class User(Base, ModificationTimesMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: str = Column(Text, unique=True, nullable=False)
    pw_hash: str = Column(Text, nullable=False)
