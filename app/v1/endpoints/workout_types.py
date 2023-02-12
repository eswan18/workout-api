from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.workout_type import WorkoutTypeIn, WorkoutTypeInDB
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db, model_id_exists

router = APIRouter(prefix="/workout_types")


@router.get("/")
def workout_types(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[WorkoutTypeInDB]:
    """
    Fetch all accessible workout types.
    """
    all_wts: list[db_models.WorkoutType] = db.query(db_models.WorkoutType).all()

    # Only return records that are owned by this user or "public", meaning their owner
    # field is null.
    def is_public_or_theirs(wt: db_models.WorkoutType) -> bool:
        return wt.owner_user_id is None or wt.owner_user_id == current_user.id

    accessible_wts = filter(is_public_or_theirs, all_wts)

    records = [WorkoutTypeInDB.from_orm(row) for row in accessible_wts]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WorkoutTypeInDB)
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
        if not model_id_exists(Model=db_models.WorkoutType, id=parent_id, db=db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"workout type with id {parent_id} does not exist",
            )

    workout_type_record = db_models.WorkoutType(**workout_type.dict())
    db.add(workout_type_record)
    db.commit()
    db.refresh(workout_type_record)
    return workout_type_record
