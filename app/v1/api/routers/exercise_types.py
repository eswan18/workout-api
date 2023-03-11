from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import sessionmaker, Session

from app.v1.models.exercise_type import ExerciseTypeInDB, ExerciseTypeIn
from app.v1.auth import get_current_user
from app import db
from app.v1.api.error_handlers import handle_db_errors
from app.v1.api.unset import _Unset, _unset


router = APIRouter(prefix="/exercise_types")


@router.get("/", response_model=list[ExerciseTypeInDB])
def read_exercise_types(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.ExerciseType]:
    """
    Fetch exercise types.
    """
    query = db.ExerciseType.query(
        current_user=current_user,
        id=id,
        name=name,
        owner_user_id=owner_user_id,
    )
    with session_factory() as session:
        result = session.scalars(query)
        return list(result)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=list[ExerciseTypeInDB]
)
def create_exercise_types(
    exercise_type: ExerciseTypeIn | list[ExerciseTypeIn],
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.ExerciseType]:
    """
    Create a new exercise type or exercise types.
    """
    if not isinstance(exercise_type, list):
        ex_tps = [exercise_type]
    else:
        ex_tps = exercise_type

    records = [ex_tp.to_orm_model(owner_user_id=current_user.id) for ex_tp in ex_tps]
    with session_factory(expire_on_commit=False) as session:
        with handle_db_errors(session):
            session.add_all(records)
            session.commit()
    return records


@router.put("/", status_code=status.HTTP_200_OK, response_model=ExerciseTypeInDB)
def overwrite_exercise_type(
    id: UUID,
    exercise_type: ExerciseTypeIn,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.ExerciseType:
    # Filter on ID and read permissions.
    query = db.ExerciseType.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"exercise type with id '{id}' not found"
            )
        if not record.updateable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update exercise type with id '{id}'",
            )
        # Update the record in-place.
        exercise_type.update_orm_model(record)
        with handle_db_errors(session):
            session.add(record)
            session.commit()
    return record


@router.patch("/", status_code=status.HTTP_200_OK, response_model=ExerciseTypeInDB)
def update_exercise_type(
    id: UUID,
    name: str = Body(_unset),
    number_of_weights: int = Body(_unset),
    notes: str | None = Body(_unset),
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.ExerciseType:
    # Filter on ID and read permissions.
    query = db.ExerciseType.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"exercise type with id '{id}' not found"
            )
        if not record.updateable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update exercise type with id '{id}'",
            )

        if not isinstance(name, _Unset):
            record.name = name
        if not isinstance(number_of_weights, _Unset):
            record.number_of_weights = number_of_weights
        if not isinstance(notes, _Unset):
            record.notes = notes

        with handle_db_errors(session):
            session.add(record)
            session.commit()

    return record


@router.delete("/", status_code=status.HTTP_200_OK, response_model=ExerciseTypeInDB)
def delete_exercise_type(
    id: UUID,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> db.ExerciseType:
    """Soft-delete an exercise type."""
    # Filter on ID and read permissions.
    query = db.ExerciseType.query(current_user=current_user, id=id)
    with session_factory(expire_on_commit=False) as session:
        record = session.scalars(query).one_or_none()
        if record is None:
            raise HTTPException(
                status_code=404, detail=f"exercise type with id '{id}' not found"
            )
        if not record.deleteable_by(current_user):
            raise HTTPException(
                status_code=401,
                detail=f"you do not have permissions to update exercise type with id '{id}'",
            )
        record.deleted_at = datetime.now(tz=timezone.utc)
        with handle_db_errors(session):
            session.commit()

    return record
