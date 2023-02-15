from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

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
    records = [SetInDB.from_orm(row) for row in result]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[SetInDB])
def create_set(
    set_: SetIn | list[SetIn],
    session: Session = Depends(db.get_db),
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
    session.add_all(records)
    session.commit()
    return records
