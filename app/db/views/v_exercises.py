from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy.engine.row import Row
from pydantic import BaseModel

from app.db.models import User


class VExercise(BaseModel):
    id: UUID
    start_time: datetime | None
    weight: float | None
    weight_unit: str | None
    reps: int | None
    seconds: int | None
    notes: str | None
    workout_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    exercise_type_id: UUID
    exercise_type_name: str
    number_of_weights: int | None
    exercise_type_notes: str | None
    exercise_type_owner_user_id: UUID | None


def get_v_exercises_by_workout_id(
    current_user: User, workout_id: UUID, session: Session
) -> list[VExercise]:
    query = text(
        """
        SELECT
            id,
            start_time,
            weight,
            weight_unit,
            reps,
            seconds,
            notes,
            workout_id,
            user_id,
            created_at,
            updated_at,
            deleted_at,
            exercise_type_id,
            exercise_type_name,
            number_of_weights,
            exercise_type_notes,
            exercise_type_owner_user_id
        FROM v_exercises
        WHERE workout_id = :workout_id
        AND user_id = :user_id
    """
    ).bindparams(workout_id=workout_id, user_id=current_user.id)
    result = session.execute(query).all()

    def row_as_exercise(row: Row) -> VExercise:
        return VExercise(
            id=row.id,
            start_time=row.start_time,
            weight=row.weight,
            weight_unit=row.weight_unit,
            reps=row.reps,
            seconds=row.seconds,
            notes=row.notes,
            workout_id=row.workout_id,
            user_id=row.user_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
            exercise_type_id=row.exercise_type_id,
            exercise_type_name=row.exercise_type_name,
            number_of_weights=row.number_of_weights,
            exercise_type_notes=row.exercise_type_notes,
            exercise_type_owner_user_id=row.exercise_type_owner_user_id,
        )

    return [row_as_exercise(row) for row in result]
