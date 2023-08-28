from uuid import UUID
from datetime import datetime
from typing import Literal

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel

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
