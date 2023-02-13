import uuid

from sqlalchemy import Text, UUID
from sqlalchemy.orm import mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin


class User(Base, ModificationTimesMixin):
    __tablename__ = "users"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = mapped_column(Text, unique=True, nullable=False)
    pw_hash = mapped_column(Text, nullable=False)
