from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

from app.v1.models.set import SetIn, SetInDB
from app.v1.auth import get_current_user
from app import db

router = APIRouter(prefix="/sets")


@router.get("/", response_model=list[SetInDB])
def read_sets(
    id: UUID | None = None,
    exercise_type_id: UUID | None = None,
    workout_id: UUID | None = None,
    min_start_time: datetime | None = None,
    max_start_time: datetime | None = None,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> list[db.Set]:
    """
    Fetch sets.
    """
    param_filter = db.Set.param_filter(
        id=id,
        exercise_type_id=exercise_type_id,
        workout_id=workout_id,
        min_start_time=min_start_time,
        max_start_time=max_start_time,
    )
    readable_filter = db.Set.read_permissions_filter(current_user)
    query = select(db.Set).where(param_filter & readable_filter)

    result = session.scalars(query)
    return list(result)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[SetInDB])
def create_sets(
    set_: SetIn | list[SetIn],
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[db.Set]:
    """
    Create a new set or sets.
    """
    if not isinstance(set_, list):
        sets = [set_]
    else:
        sets = set_

    records = [db.Set(**s.dict(), user_id=current_user.id) for s in sets]
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
