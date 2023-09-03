from uuid import UUID
from datetime import datetime
from typing import Literal

from sqlalchemy.orm import Session
from sqlalchemy.sql import select, text, desc
from sqlalchemy.schema import Table
from sqlalchemy.sql.elements import UnaryExpression
from pydantic import BaseModel
from app.db.database import Base, get_engine

from app.db.models import User


class VWorkout(BaseModel):
    id: UUID
    start_time: datetime
    end_time: datetime | None
    status: Literal["in-progress", "paused", "completed"]
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    workout_type_id: UUID | None
    workout_type_name: str | None
    workout_type_notes: str | None
    parent_workout_type_id: UUID | None
    workout_type_owner_user_id: UUID | None


engine = get_engine()
v_workouts = Table("v_workouts", Base.metadata, autoload_with=engine)


def get_v_workout_by_workout_id(
    current_user: User, workout_id: UUID, session: Session
) -> VWorkout | None:
    query = text(
        """
        SELECT
            id,
            start_time,
            end_time,
            status,
            user_id,
            created_at,
            updated_at,
            deleted_at,
            workout_type_id,
            workout_type_name,
            workout_type_notes,
            parent_workout_type_id,
            workout_type_owner_user_id
        FROM v_workouts
        WHERE id = :workout_id
        AND user_id = :user_id
    """
    ).bindparams(workout_id=workout_id, user_id=current_user.id)
    result = session.execute(query).one_or_none()
    if result is None:
        return None

    return VWorkout(
        id=result.id,
        start_time=result.start_time,
        end_time=result.end_time,
        status=result.status,
        user_id=result.user_id,
        created_at=result.created_at,
        updated_at=result.updated_at,
        deleted_at=result.deleted_at,
        workout_type_id=result.workout_type_id,
        workout_type_name=result.workout_type_name,
        workout_type_notes=result.workout_type_notes,
        parent_workout_type_id=result.parent_workout_type_id,
        workout_type_owner_user_id=result.workout_type_owner_user_id,
    )


def get_v_workouts_sorted(
    current_user: User,
    session: Session,
    order_by: str = "start_time",
    asc: bool = True,
    limit: int = 10,
) -> list[VWorkout]:
    order_by_clause: str | UnaryExpression = order_by if asc else desc(order_by)
    query = (
        select(v_workouts)
        .where(v_workouts.c.user_id == current_user.id)
        .order_by(order_by_clause)
        .limit(limit)
    )

    result = session.execute(query)

    def record_as_workout(record):
        return VWorkout(
            id=record.id,
            start_time=record.start_time,
            end_time=record.end_time,
            status=record.status,
            user_id=record.user_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            deleted_at=record.deleted_at,
            workout_type_id=record.workout_type_id,
            workout_type_name=record.workout_type_name,
            workout_type_notes=record.workout_type_notes,
            parent_workout_type_id=record.parent_workout_type_id,
            workout_type_owner_user_id=record.workout_type_owner_user_id,
        )

    return [record_as_workout(record) for record in result]
