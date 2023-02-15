import uuid
from typing import Self

from sqlalchemy.sql import Select
from sqlalchemy.types import Text, UUID
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User


class WorkoutType(Base, ModificationTimesMixin):
    __tablename__ = "workout_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    # Foreign keys
    parent_workout_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_types.id")
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    # Relationships
    children: Mapped[list["WorkoutType"]] = relationship(
        "WorkoutType", backref=backref("parent_workout_type", remote_side=[id])
    )
    owner: Mapped[User] = relationship(User, backref="owned_workout_types")

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
            query = query.where(cls.id == id)
        if name is not None:
            query = query.where(cls.name == name)
        if owner_user_id is not None:
            query = query.where(cls.owner_user_id == owner_user_id)
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
        return query.filter((cls.owner == None) | (cls.owner == user))
