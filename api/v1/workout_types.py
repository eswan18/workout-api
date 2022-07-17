from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .models.workout_type import WorkoutTypeIn, WorkoutTypeInDB
from .auth import get_current_user
from ..db import models as db_models
from ..db import get_db

router = APIRouter(prefix="/workout_types")


@router.get("/")
def workout_types(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[WorkoutTypeInDB]:
    """
    Fetch all workout types.
    """
    result = db.query(db_models.WorkoutType).all()
    records = [WorkoutTypeInDB.from_orm(row) for row in result]
    return records


@router.post("/")
def create_workout_type(
    workout_type: WorkoutTypeIn,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> db_models.WorkoutType:
    """
    Create a new workout type.
    """
    # Make sure that the parent workout type ID, if included, is in the DB.
    parent_id = workout_type.parent_workout_type_id
    if parent_id is not None:
        if db.query(db_models.WorkoutType.id).filter_by(id=parent_id).first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"workout type with id {parent_id} does not exist",
            )

    workout_type_record = db_models.WorkoutType(**workout_type.dict())
    db.add(workout_type_record)
    db.commit()
    db.refresh(workout_type_record)
    return workout_type_record
