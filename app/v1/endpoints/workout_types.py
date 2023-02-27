from datetime import datetime, timezone
from uuid import UUID

from pydantic.fields import Undefined, UndefinedType
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.sql import select
from sqlalchemy.orm import Session, sessionmaker

from app.v1.models.workout_type import WorkoutTypeIn, WorkoutTypeInDB
from app.v1.auth import get_current_user
from app import db
from .error_handlers import handle_db_errors

router = APIRouter(prefix="/workout_types")


@router.get("/", response_model=list[WorkoutTypeInDB])
def workout_types(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.WorkoutType]:
    """
    Fetch workout types.
    """
    query = db.WorkoutType.build_query(
        current_user=current_user, id=id, name=name, owner_user_id=owner_user_id
    )
    with session_factory() as session:
        result = session.scalars(query)
        return list(result)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=list[WorkoutTypeInDB]
)
def create_workout_type(
    workout_type: WorkoutTypeIn | list[WorkoutTypeIn],
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.WorkoutType]:
    """
    Create a new workout type or workout types.
    """
    if not isinstance(workout_type, list):
        wkt_tps = [workout_type]
    else:
        wkt_tps = workout_type

    records = [wk_tp.to_orm_model(owner_user_id=current_user.id) for wk_tp in wkt_tps]
    with session_factory(expire_on_commit=False) as session:
        with handle_db_errors(session):
            session.add_all(records)
            session.commit()
    return records


@router.put("/", status_code=status.HTTP_200_OK, response_model=WorkoutTypeInDB)
def overwrite_workout_type(
    id: UUID,
    workout_type: WorkoutTypeIn,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.WorkoutType:
    # Filter on ID and read permissions.
    query = db.WorkoutType.build_query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"workout type with id '{id}' not found"
            )
        if not record.updateable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update workout type with id '{id}'",
            )
        # Update the record in-place.
        workout_type.update_orm_model(record)
        with handle_db_errors(session):
            session.add(record)
            session.commit()
    return record


@router.patch("/", status_code=status.HTTP_200_OK, response_model=WorkoutTypeInDB)
def update_workout_type(
    id: UUID,
    name: str = Body(Undefined),
    notes: str | None = Body(Undefined),
    parent_workout_type_id: UUID | None = Body(Undefined),
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.WorkoutType:
    # I'll come back to this later but PUT alone is enough for MVP.
    raise HTTPException(status_code=501, detail="Patch endpoints not implemented yet.")
    # Filter on ID and read permissions.
    query = (
        select(db.WorkoutType)
        .filter_by(id=id)
        .where(db.WorkoutType.readable_by(current_user))
        .where(db.WorkoutType.not_soft_deleted())
    )
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"workout type with id '{id}' not found"
            )
        if not record.updateable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update workout type with id '{id}'",
            )

        if not isinstance(name, UndefinedType):
            record.name = name
        if not isinstance(notes, UndefinedType):
            record.notes = notes
        if not isinstance(parent_workout_type_id, UndefinedType):
            record.parent_workout_type_id = parent_workout_type_id
        session.commit()

    return record


@router.delete("/", status_code=status.HTTP_200_OK, response_model=WorkoutTypeInDB)
def soft_delete_workout_type(
    id: UUID,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.WorkoutType:
    """Soft-delete a workout type"""
    # Filter on ID and read permissions.
    query = db.WorkoutType.build_query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"workout type with id '{id}' not found"
            )
        if not record.deleteable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update workout type with id '{id}'",
            )
        record.deleted_at = datetime.now(tz=timezone.utc)
        session.commit()

    return record
