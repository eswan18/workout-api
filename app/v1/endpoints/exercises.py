from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import sessionmaker, Session

from app.v1.models.exercise import ExerciseIn, ExerciseInDB
from app.v1.auth import get_current_user
from app import db
from .error_handlers import handle_db_errors
from app.unset import _Unset, _unset

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
    query = db.Exercise.query(
        current_user=current_user,
        id=id,
        exercise_type_id=exercise_type_id,
        workout_id=workout_id,
        min_start_time=min_start_time,
        max_start_time=max_start_time,
    )
    with session_factory() as session:
        result = session.scalars(query)
        return list(result)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=list[ExerciseInDB]
)
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

    records = [ex.to_orm_model(user_id=current_user.id) for ex in exercises]
    with session_factory(expire_on_commit=False) as session:
        with handle_db_errors(session):
            session.add_all(records)
            session.commit()
    return records


@router.put("/", status_code=status.HTTP_200_OK, response_model=ExerciseInDB)
def overwrite_exercise(
    id: UUID,
    exercise: ExerciseIn,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.Exercise:
    query = db.Exercise.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"workout with id '{id}' not found"
            )
        if not record.updateable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update workout with id '{id}'",
            )
        # Update the record in-place.
        exercise.update_orm_model(record)
        with handle_db_errors(session):
            session.add(record)
            session.commit()
    return record


@router.patch("/", status_code=status.HTTP_200_OK, response_model=ExerciseInDB)
def update_exercise(
    id: UUID,
    start_time: datetime | None = Body(_unset),
    weight: float = Body(_unset),
    weight_unit: str | None = Body(_unset),
    reps: int | None = Body(_unset),
    seconds: int | None = Body(_unset),
    notes: str | None = Body(_unset),
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.Exercise:
    # Filter on ID and read permissions.
    query = db.Exercise.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"exercise with id '{id}' not found"
            )
        if not record.updateable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update exercise with id '{id}'",
            )

        if not isinstance(start_time, _Unset):
            record.start_time = start_time
        if not isinstance(weight, _Unset):
            record.weight = weight
        if not isinstance(weight_unit, _Unset):
            record.weight_unit = weight_unit
        if not isinstance(reps, _Unset):
            record.reps = reps
        if not isinstance(seconds, _Unset):
            record.seconds = seconds
        if not isinstance(notes, _Unset):
            record.notes = notes

        with handle_db_errors(session):
            session.add(record)
            session.commit()

    return record


@router.delete("/", status_code=status.HTTP_200_OK, response_model=ExerciseInDB)
def delete_exercise(
    id: UUID,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.Exercise:
    """Soft-delete an exercise."""
    # Filter on ID and read permissions.
    query = db.Exercise.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"exercise with id '{id}' not found"
            )
        if not record.deleteable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update exercise with id '{id}'",
            )
        record.deleted_at = datetime.now(tz=timezone.utc)
        with handle_db_errors(session):
            session.commit()

    return record
