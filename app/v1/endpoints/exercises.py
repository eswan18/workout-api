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
    Fetch all exercises.
    """
    result = db.query(db_models.Exercise).all()
    records = [ExerciseInDB.from_orm(row) for row in result]
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
    db.add(exercise_record)
    db.commit()
    db.refresh(exercise_record)
    return exercise_record
