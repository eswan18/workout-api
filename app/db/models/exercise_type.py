import uuid
from typing import Self

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, Text, UUID
from sqlalchemy.sql.elements import BooleanClauseList, ColumnElement
from sqlalchemy.sql import Select, select, and_
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
    def param_filter(
        cls,
        *,
        id: uuid.UUID | None = None,
        name: str | None = None,
        owner_user_id: uuid.UUID | None = None,
    ) -> ColumnElement[bool]:
        """Build a filter over user-supplied parameters"""
        f = and_(True)  # Wrapping True in `and_` helps with typing issues.
        if id is not None:
            f = and_(f, cls.id == id)
        if name is not None:
            f = and_(cls.name == name)
        if owner_user_id is not None:
            f = and_(cls.owner_user_id == owner_user_id)
        return f

    @classmethod
    def readable_by(
        cls,
        user: User,
    ) -> BooleanClauseList:
        """Build a filter for exercise types this user can read."""
        # Users can access exercise types that they own or that are public, denoted as a
        # null value in owner_user_id.
        return (cls.owner == user) | (cls.owner == None)

    def updateable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this exercise type can be updated by this user."""
        # n.b. Comparing (self.owner == user) doesn't work; I haven't figured out why.
        return self.owner_user_id == user.id

    def deleteable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this exercise type can be deleted by this user."""
        # n.b. Comparing (self.owner == user) doesn't work; I haven't figured out why.
        return self.owner_user_id == user.id

    @classmethod
    def not_soft_deleted(cls) -> ColumnElement[bool]:
        """Build a filter for not-soft-deleted."""
        return cls.deleted_at == None

    @classmethod
    def query(
        cls,
        current_user: User,
        *,
        id: uuid.UUID | None = None,
        name: str | None = None,
        owner_user_id: uuid.UUID | None = None,
        include_soft_deleted: bool = False,
    ) -> Select[tuple[Self]]:
        """
        Build a query to filter all the resources accessible to this user.
        """
        query = (
            select(cls)
            .where(cls.param_filter(id=id, name=name, owner_user_id=owner_user_id))
            .where(cls.readable_by(current_user))
        )
        if not include_soft_deleted:
            query = query.where(cls.not_soft_deleted())
        return query
