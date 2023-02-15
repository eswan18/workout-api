import uuid
from typing import Self

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, Text, UUID
from sqlalchemy.sql import Select
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User


class ExerciseType(Base, ModificationTimesMixin):
    __tablename__ = "exercise_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text)
    number_of_weights: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text)
    # Foreign keys
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    # Relationships
    owner: Mapped[User] = relationship(User, backref="owned_exercises")

    @classmethod
    def apply_params(
        cls,
        query: Select[tuple[Self]],
        *,
        id: uuid.UUID | None = None,
        name: str | None = None,
        owner_user_id: uuid.UUID | None = None,
    ) -> Select[tuple[Self]]:
        if id is not None:
            query = query.filter(cls.id == id)
        if name is not None:
            query = query.filter(cls.name == name)
        if owner_user_id is not None:
            query = query.filter(cls.owner_user_id == owner_user_id)
        return query

    @classmethod
    def apply_read_permissions(
        cls,
        query: Select[tuple[Self]],
        user: User,
    ) -> Select[tuple[Self]]:
        """
        Limit a query down to only the resources a user has access to read.
        """
        # Users can access workout types that they own or that are public, denoted as a
        # null value in owner_user_id.
        return query.where((cls.owner == user) | (cls.owner == None))  # noqa
