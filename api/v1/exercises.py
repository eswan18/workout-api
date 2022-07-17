from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .models.exercise import ExerciseInDB
from .auth import get_current_user
from ..db import models as db_models
from ..db import get_db

router = APIRouter(prefix="/exercises")


@router.get("/", response_model=list[ExerciseInDB])
def exercises(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[ExerciseInDB]:
    result = db.query(db_models.Exercise).all()
    records = [ExerciseInDB.from_orm(row) for row in result]
    return records
