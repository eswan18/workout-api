import uuid

from sqlalchemy import Text, UUID
from sqlalchemy.orm import mapped_column, Mapped

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin


class User(Base, ModificationTimesMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(Text, unique=True)
    pw_hash: Mapped[str] = mapped_column(Text)
