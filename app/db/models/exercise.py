from typing import Self, Iterable
import uuid
from datetime import datetime

from sqlalchemy.schema import CheckConstraint, ForeignKey
from sqlalchemy.types import Integer, Double, Text, DateTime, UUID
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql import Select, select, and_, values, column, literal, or_
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin
from .user import User
from .workout import Workout
from .exercise_type import ExerciseType


class Exercise(Base, ModificationTimesMixin):
    __tablename__ = "exercises"
    __table_args__ = (
        # Users can only create exercises in their own workouts.
        CheckConstraint("user_id = workout.user_id"),
        # Users can only create exercises of types they own or of public types.
        CheckConstraint(
            "user_id = exercise_type.user_id OR exercise_type.user_id IS NULL"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    weight: Mapped[float | None] = mapped_column(Double)
    weight_unit: Mapped[str | None] = mapped_column(Text)
    reps: Mapped[int | None] = mapped_column(Integer)
    seconds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    # Foreign keys
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id")
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workouts.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    # Relationships
    exercise_type: Mapped[ExerciseType] = relationship(
        "ExerciseType", backref="exercises"
    )
    workout: Mapped[Workout] = relationship("Workout", backref="exercises")
    user: Mapped[User] = relationship("User", backref="exercises")

    @classmethod
    def param_filter(
        cls,
        *,
        id: uuid.UUID | None = None,
        exercise_type_id: uuid.UUID | None = None,
        workout_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
    ) -> ColumnElement[bool]:
        """Build a filter over user-supplied parameters"""
        f = and_(True)  # Wrapping True in `and_` helps with typing issues.
        if id is not None:
            f = and_(f, cls.id == id)
        if exercise_type_id is not None:
            f = and_(f, cls.exercise_type_id == exercise_type_id)
        if workout_id is not None:
            f = and_(f, cls.workout_id == workout_id)
        if user_id is not None:
            f = and_(f, cls.user_id == user_id)
        if min_start_time is not None:
            f = and_(f, cls.start_time > min_start_time)
        if max_start_time is not None:
            f = and_(f, cls.start_time < max_start_time)
        return f

    @classmethod
    def readable_by(
        cls,
        user: User,
    ) -> ColumnElement[bool]:
        """Build a filter for exercises this user can read."""
        return cls.user == user

    def updateable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this exercise can be updated by this user."""
        # n.b. Comparing (self.user == user) doesn't work; I haven't figured out why.
        return self.user_id == user.id

    def deleteable_by(
        self,
        user: User,
    ) -> bool:
        """Determine if this exercise can be deleted by this user."""
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
        exercise_type_id: uuid.UUID | None = None,
        workout_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        min_start_time: datetime | None = None,
        max_start_time: datetime | None = None,
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
                    exercise_type_id=exercise_type_id,
                    workout_id=workout_id,
                    user_id=user_id,
                    min_start_time=min_start_time,
                    max_start_time=max_start_time,
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
    ) -> Select[tuple[str, UUID]]:
        """
        Return a Select of referenced workouts/exercise types that aren't in the db.

        Result rows are tuples of (parent_type, parent_id).
        """
        workout_ids = values(column("id", UUID), name="workout_ids").data(
            [(r.workout_id,) for r in records]
        )
        workout_query = (
            select(column("id").label("ref_id"), literal("workout").label("ref_type"))
            .select_from(workout_ids)
            .where(
                column("id").not_in(
                    select(Workout.id).where(Workout.user_id == user.id)
                )
            )
        )

        ex_tp_ids = values(column("id", UUID), name="exercise_type_ids").data(
            [(r.exercise_type_id,) for r in records]
        )
        ex_tp_query = (
            select(
                column("id").label("ref_id"),
                literal("exercise_type").label("ref_type"),
            )
            .select_from(
                ex_tp_ids,
            )
            .where(
                column("id").not_in(
                    select(ExerciseType.id).where(
                        # Note: doing .owner_user_id.in_((user.id, None)) here doesn't
                        # work; we need the OR for some reason.
                        or_(
                            ExerciseType.owner_user_id == user.id,
                            ExerciseType.owner_user_id.is_(None),
                        ),
                    )
                )
            )
        )

        query = workout_query.union_all(ex_tp_query)
        return query
