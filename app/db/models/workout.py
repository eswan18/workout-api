from typing import Self, Iterable
import uuid
from datetime import datetime

from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime, Text, UUID
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql import select, Select, and_
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .workout_type import WorkoutType
from .user import User
from ._common import missing_references_to_model_query


class Workout(Base, ModificationTimesMixin):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    # Foreign keys
    workout_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_types.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    # Relationships
    workout_type: Mapped[WorkoutType] = relationship("WorkoutType", backref="workouts")
    user: Mapped[User] = relationship("User", backref="workouts")

    @classmethod
    def param_filter(
        cls,
        *,
        id: uuid.UUID | None = None,
        status: str | None = None,
        workout_type_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
        min_end_time: datetime | None = None,
        max_end_time: datetime | None = None,
    ) -> ColumnElement[bool]:
        """Build a filter over user-supplied parameters"""
        f = and_(True)  # Wrapping True in `and_` helps with typing issues.
        if id is not None:
            f = and_(f, cls.id == id)
        if status is not None:
            f = and_(f, cls.status == status)
        if workout_type_id is not None:
            f = and_(cls.workout_type_id == workout_type_id)
        if user_id is not None:
            f = and_(f, cls.user_id == user_id)
        if min_start_time is not None:
            f = and_(f, cls.start_time > min_start_time)
        if max_start_time is not None:
            f = and_(f, cls.start_time < max_start_time)
        if min_end_time is not None:
            f = and_(f, cls.end_time > min_end_time)
        if max_end_time is not None:
            f = and_(f, cls.end_time < max_end_time)
        return f

    @classmethod
    def readable_by(
        cls,
        user: User,
    ) -> ColumnElement[bool]:
        """Build a filter for workouts this user can read."""
        return cls.user == user

    def updateable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this workout can be updated by this user."""
        # n.b. Comparing (self.user == user) doesn't work; I haven't figured out why.
        return self.user_id == user.id

    def deleteable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this workout can be deleted by this user."""
        # n.b. Comparing (self.user == user) doesn't work; I haven't figured out why.
        return self.user_id == user.id

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
        status: str | None = None,
        workout_type_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
        min_end_time: datetime | None = None,
        max_end_time: datetime | None = None,
        include_soft_deleted: bool = False,
    ) -> Select[tuple[Self]]:
        """
        Build a query to filter all the resources accessible to this user.
        """
        query = (
            select(cls)
            .where(
                cls.param_filter(
                    id=id,
                    status=status,
                    workout_type_id=workout_type_id,
                    user_id=user_id,
                    min_start_time=min_start_time,
                    max_start_time=max_start_time,
                    min_end_time=min_end_time,
                    max_end_time=max_end_time,
                )
            )
            .where(cls.readable_by(current_user))
        )
        if not include_soft_deleted:
            query = query.where(cls.not_soft_deleted())
        return query

    @classmethod
    def missing_references_query(
        cls, records: Iterable[Self], user: User
    ) -> Select[tuple[uuid.UUID, str]]:
        """
        Return a Select of referenced workouts types that aren't in the db.

        Result rows are tuples of ('workout_type', parent_id).
        """
        missing_ex_tps_query = missing_references_to_model_query(
            ids=(r.workout_type_id for r in records if r.workout_type_id is not None),
            user=user,
            model=WorkoutType,
        )
        return missing_ex_tps_query
