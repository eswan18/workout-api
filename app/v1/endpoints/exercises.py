from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..models.exercise import ExerciseInDB, ExerciseIn
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db

router = APIRouter(prefix="/exercises")


@router.get("/", response_model=list[ExerciseInDB])
def exercises(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[ExerciseInDB]:
    """
    Fetch all accessible exercises.
    """
    all_ex = db.query(db_models.Exercise).all()

    # Only return records that are owned by this user or "public", meaning their owner
    # field is null.
    def is_public_or_theirs(ex: db_models.Exercise) -> bool:
        return ex.owner_user_id is None or ex.owner_user_id == current_user.id

    accessible_ex = filter(is_public_or_theirs, all_ex)

    records = [ExerciseInDB.from_orm(row) for row in accessible_ex]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ExerciseInDB)
def create_exercise(
    exercise: ExerciseIn,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> db_models.Exercise:
    """
    Create a new exercise.
    """
    exercise_record = db_models.Exercise(**exercise.dict())
    exercise_record.owner_user_id = current_user.id
    db.add(exercise_record)
    db.commit()
    db.refresh(exercise_record)
    return exercise_record
