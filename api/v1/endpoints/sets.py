from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..models.set import SetIn, SetInDB
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db

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


@router.post("/")
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
    id_and_model_class = [
        (set_dict["exercise_id"], db_models.Exercise),
        (set_dict["workout_id"], db_models.Workout),
    ]
    for id, model in id_and_model_class:
        if db.query(model).filter_by(id=id).first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} with id {id} does not exist",
            )

    set_record = db_models.Set(**set_dict)
    db.add(set_record)
    db.commit()
    db.refresh(set_record)
    return set_record
