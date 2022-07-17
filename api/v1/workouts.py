from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .models.workout import Workout, WorkoutInDB
from .auth import get_current_user
from ..db import models as db_models
from ..db import get_db

router = APIRouter(prefix="/workouts")


@router.get("/", response_model=list[WorkoutInDB])
def workouts(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[WorkoutInDB]:
    result = db.query(db_models.Workout).filter_by(user=current_user).all()
    records = [WorkoutInDB.from_orm(row) for row in result]
    return records


@router.post("/", response_model=WorkoutInDB)
def create_workout(
    workout: Workout,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> WorkoutInDB:
    workout_record = db_models.Workout(**workout)
