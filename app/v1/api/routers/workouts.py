from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import Session, sessionmaker

from app.v1.models.workout import WorkoutIn, WorkoutInDB
from app.v1.auth import get_current_user
from app import db
from app.v1.api.error_handlers import handle_db_errors
from app.v1.api.unset import _Unset, _unset

router = APIRouter(prefix="/workouts")


@router.get("/", response_model=list[WorkoutInDB])
def read_workouts(
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
    query = db.Workout.query(
        current_user=current_user,
        id=id,
        status=status,
        workout_type_id=workout_type_id,
        min_start_time=min_start_time,
        max_start_time=max_start_time,
        min_end_time=min_end_time,
        max_end_time=max_end_time,
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

    records = [wkt.to_orm_model(user_id=current_user.id) for wkt in wkts]
    with session_factory(expire_on_commit=False) as session:
        with handle_db_errors(session):
            session.add_all(records)
            session.commit()
    return records


@router.put("/", status_code=status.HTTP_200_OK, response_model=WorkoutInDB)
def overwrite_workout(
    id: UUID,
    workout: WorkoutIn,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.Workout:
    # Filter on ID and read permissions.
    query = db.Workout.query(current_user=current_user, id=id)
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
        workout.update_orm_model(record)
        with handle_db_errors(session):
            session.add(record)
            session.commit()
    return record


@router.patch("/", status_code=status.HTTP_200_OK, response_model=WorkoutInDB)
def update_workout(
    id: UUID,
    start_time: datetime | None = Body(_unset),
    end_time: datetime | None = Body(_unset),
    status: str = Body(_unset),
    notes: str | None = Body(_unset),
    workout_type_id: UUID | None = Body(_unset),
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.Workout:
    # Filter on ID and read permissions.
    query = db.Workout.query(current_user=current_user, id=id)
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

        if not isinstance(start_time, _Unset):
            record.start_time = start_time
        if not isinstance(end_time, _Unset):
            record.end_time = end_time
        if not isinstance(status, _Unset):
            record.status = status
        if not isinstance(notes, _Unset):
            record.notes = notes
        if not isinstance(workout_type_id, _Unset):
            record.workout_type_id = workout_type_id

        with handle_db_errors(session):
            session.add(record)
            session.commit()

    return record


@router.delete("/", status_code=status.HTTP_200_OK, response_model=WorkoutInDB)
def delete_workout(
    id: UUID,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.Workout:
    """Soft-delete a workout."""
    # Filter on ID and read permissions.
    query = db.Workout.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"workout with id '{id}' not found"
            )
        if not record.deleteable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update workout with id '{id}'",
            )
        record.deleted_at = datetime.now(tz=timezone.utc)
        with handle_db_errors(session):
            session.commit()

    return record
