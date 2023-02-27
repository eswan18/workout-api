from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

from app.v1.models.exercise import ExerciseIn, ExerciseInDB
from app.v1.auth import get_current_user
from app import db

router = APIRouter(prefix="/exercises")


@router.get("/", response_model=list[ExerciseInDB])
def read_exercises(
    id: UUID | None = None,
    exercise_type_id: UUID | None = None,
    workout_id: UUID | None = None,
    min_start_time: datetime | None = None,
    max_start_time: datetime | None = None,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.Exercise]:
    """
    Fetch exercises.
    """
    param_filter = db.Exercise.param_filter(
        id=id,
        exercise_type_id=exercise_type_id,
        workout_id=workout_id,
        min_start_time=min_start_time,
        max_start_time=max_start_time,
    )
    query = select(db.Exercise).where(param_filter).where(db.Exercise.readable_by(current_user))

    with session_factory() as session:
        result = session.scalars(query)
        return list(result)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[ExerciseInDB])
def create_exercises(
    exercise: ExerciseIn | list[ExerciseIn],
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.Exercise]:
    """
    Create a new exercise or exercises.
    """
    if not isinstance(exercise, list):
        exercises = [exercise]
    else:
        exercises = exercise

    records = [db.Exercise(**s.dict(), user_id=current_user.id) for s in exercises]
    with session_factory(expire_on_commit=False) as session:
        session.add_all(records)
        try:
            session.commit()
        except IntegrityError as exc:
            original_error = exc.orig
            if isinstance(original_error, ForeignKeyViolation):
                msg = str(original_error)
            else:
                msg = str(exc.detail)
            session.rollback()
            raise HTTPException(status_code=400, detail=msg)
    return records
