from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .models.exercise import Exercise, ExerciseInDB
from ..db import models as db_models
from ..db import get_db

router = APIRouter(
    prefix="/exercises",
    dependencies=[Depends(get_db)],
)


@router.get("/", response_model=list[Exercise])
async def exercises(db: Session = Depends(get_db)):
    result = db.query(db_models.Exercise).all()
    records = [ExerciseInDB.from_orm(row) for row in result]
    return records
