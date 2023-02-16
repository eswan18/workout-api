from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.sql import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from psycopg2.errors import ForeignKeyViolation

from app.v1.models.workout_type import WorkoutTypeIn, WorkoutTypeInDB
from app.v1.auth import get_current_user
from app import db

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
    param_filter = db.WorkoutType.param_filter(
        id=id, name=name, owner_user_id=owner_user_id
    )
    permissions_filter = db.WorkoutType.read_permissions_filter(current_user)
    query = select(db.WorkoutType).filter(param_filter & permissions_filter)

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
    Create a new workout type or workout types..
    """
    if not isinstance(workout_type, list):
        wkt_tps = [workout_type]
    else:
        wkt_tps = workout_type

    records = [
        db.WorkoutType(**wk.dict(), owner_user_id=current_user.id) for wk in wkt_tps
    ]
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
