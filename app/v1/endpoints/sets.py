from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from app.v1.models.set import SetIn, SetInDB
from app.v1.auth import get_current_user
from app import db

router = APIRouter(prefix="/sets")


@router.get("/")
def sets(
    id: UUID | None = None,
    exercise_type_id: UUID | None = None,
    workout_id: UUID | None = None,
    min_start_time: datetime | None = None,
    max_start_time: datetime | None = None,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> list[SetInDB]:
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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SetInDB)
def create_set(
    set_: SetIn,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> db.Set:
    """
    Record a new set.
    """
    # Add the current user's ID to the record.
    set_dict = set_.dict()
    set_dict["user_id"] = current_user.id

    # Validate that the exercise type ID and workout ID are present in the DB.
    exercise_type_id = set_dict["exercise_type_id"]
    if not db.model_id_exists(
        Model=db.ExerciseType, id=exercise_type_id, session=session
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"exercise type with id {exercise_type_id} does not exist",
        )
    workout_id = set_dict["workout_id"]
    if not db.model_id_exists(Model=db.Workout, id=workout_id, session=session):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"workout with id {workout_id} does not exist",
        )

    set_record = db.Set(**set_dict)
    session.add(set_record)
    session.commit()
    session.refresh(set_record)
    return set_record
