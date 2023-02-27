import uuid

from typing_extensions import Self
from sqlalchemy.sql.elements import ColumnElement, BooleanClauseList
from sqlalchemy.sql import select, and_, Select
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
    owner: Mapped[User] = relationship(User, back_populates="owned_workout_types")

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
            f = and_(f, cls.name == name)
        if owner_user_id is not None:
            f = and_(f, cls.owner_user_id == owner_user_id)
        return f

    @classmethod
    def readable_by(
        cls,
        user: User,
    ) -> BooleanClauseList:
        """Build a filter for workout types this user can read."""
        # Users can access workout types that they own or that are public, denoted as a
        # null value in owner_user_id.
        return (cls.owner == user) | (cls.owner == None)

    def updateable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this workout type can be updated by this user."""
        # n.b. Comparing (self.owner == user) doesn't work; I haven't figured out why.
        return self.owner_user_id == user.id

    def deleteable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this workout type can be deleted by this user."""
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
