from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from psycopg2.errors import ForeignKeyViolation

from app.v1.models.workout import WorkoutIn, WorkoutInDB
from app.v1.auth import get_current_user
from app import db
from .error_handlers import handle_db_errors

router = APIRouter(prefix="/workouts")


@router.get("/", response_model=list[WorkoutInDB])
def workouts(
    id: UUID | None = None,
    status: str | None = None,
    workout_type_id: UUID | None = None,
    min_start_time: datetime | None = None,
    max_start_time: datetime | None = None,
    min_end_time: datetime | None = None,
    max_end_time: datetime | None = None,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.Workout]:
    """
    Fetch workouts.
    """
    param_filter = db.Workout.param_filter(
        id=id,
        status=status,
        workout_type_id=workout_type_id,
        min_start_time=min_start_time,
        max_start_time=max_start_time,
        min_end_time=min_end_time,
        max_end_time=max_end_time,
    )
    query = (
        select(db.Workout)
        .where(param_filter)
        .where(db.Workout.readable_by(current_user))
    )

    with session_factory() as session:
        result = session.scalars(query)
        return list(result)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[WorkoutInDB])
def create_workout(
    workout: WorkoutIn | list[WorkoutIn],
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.Workout]:
    """
    Record a new workout or workouts.
    """
    if not isinstance(workout, list):
        wkts = [workout]
    else:
        wkts = workout

    records = [db.Workout(**wkt.dict(), user_id=current_user.id) for wkt in wkts]
    with session_factory(expire_on_commit=False) as session:
        with handle_db_errors(session):
            session.add_all(records)
            session.commit()
    return records
