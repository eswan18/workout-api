from typing import Self, Iterable
import uuid
from datetime import datetime

from sqlalchemy.schema import CheckConstraint, ForeignKey
from sqlalchemy.types import Integer, Double, Text, DateTime, UUID
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql import Select, select, and_, text
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
    def parents_exist_and_are_readable(
        cls, exercises: Iterable[Self], user: User
    ) -> Select[tuple[bool]]:
        """
        Check if the workout and exercise type of this exercise exist and are visible.

        Useful for determining whether a user should be able to create/update an
        exercise with these parents.
        """
        query = text(
            """
            SELECT
                ids.id AS id,
                'workout' AS parent_type,
                CASE WHEN user_workouts.id IS NULL THEN false ELSE true END AS exists
            FROM (VALUES
                ('123e4567-e89b-12d3-a456-426655440000'::uuid),
                ('a8d26bbc-c6af-4d85-b019-82096b1a21af'::uuid)
            ) as ids(id)
            LEFT JOIN (
                SELECT * FROM workouts
                WHERE user_id = :user_id
            ) AS user_workouts
            ON user_workouts.id = ids.id

            UNION ALL

            SELECT
                ids.id AS id,
                'exercise_type' AS parent_type,
                CASE WHEN user_exercise_types.id IS NULL THEN false ELSE true END AS exists
            FROM (VALUES
                ('123e4567-e89b-12d3-a456-426655440000'::uuid),
                ('a8d26bbc-c6af-4d85-b019-82096b1a21af'::uuid)
            ) as ids(id)
            LEFT JOIN (
                SELECT * FROM exercise_types
                WHERE user_id = :user_id or user_id IS NULL
            ) AS user_exercise_types
            ON user_exercise_types.id = ids.id
        """
        )
        return self.workout.readable_by(user) and self.exercise_type.readable_by(user)
