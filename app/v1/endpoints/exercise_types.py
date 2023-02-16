from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from psycopg2.errors import ForeignKeyViolation

from app.v1.models.exercise_type import ExerciseTypeInDB, ExerciseTypeIn
from app.v1.auth import get_current_user
from app import db

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
    param_filter = db.ExerciseType.param_filter(
        id=id, name=name, owner_user_id=owner_user_id
    )
    readable_filter = db.ExerciseType.read_permissions_filter(current_user)
    query = select(db.ExerciseType).where(param_filter & readable_filter)

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

    records = [
        db.ExerciseType(**ex.dict(), owner_user_id=current_user.id) for ex in ex_tps
    ]
    with session_factory() as session:
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
        for record in records:
            session.refresh(record)
    return records
