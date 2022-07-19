from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..models.set import SetIn, SetInDB
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db, model_id_exists

router = APIRouter(prefix="/sets")


@router.get("/")
def sets(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[SetInDB]:
    """
    Fetch all the sets for your user.
    """
    result = db.query(db_models.Set).filter_by(user=current_user).all()
    records = [SetInDB.from_orm(row) for row in result]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SetInDB)
def create_set(
    set_: SetIn,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> db_models.Set:
    """
    Record a new set.
    """
    # Add the current user's ID to the record.
    set_dict = set_.dict()
    set_dict["user_id"] = current_user.id

    # Validate that the exercise ID and workout ID are present in the DB.
    exercise_id = set_dict["exercise_id"]
    if not model_id_exists(Model=db_models.Exercise, id=exercise_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"exercise with id {exercise_id} does not exist",
        )
    workout_id = set_dict["workout_id"]
    if not model_id_exists(Model=db_models.Workout, id=workout_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"workout with id {workout_id} does not exist",
        )

    set_record = db_models.Set(**set_dict)
    db.add(set_record)
    db.commit()
    db.refresh(set_record)
    return set_record
