from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .models.exercise import Exercise
from ..db import models as db_models
from ..db import get_db

router = APIRouter(
    prefix='/exercises',
    dependencies=[Depends(get_db)],
)


@router.get('/')
async def exercises(db: Session = Depends(get_db)) -> list[Exercise]:
    result = db.query(db_models.Exercise)
    print(result)
