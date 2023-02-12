from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..models.exercise import ExerciseInDB, ExerciseIn
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db

router = APIRouter(prefix="/exercises")


@router.get("/", response_model=list[ExerciseInDB])
def exercises(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[ExerciseInDB]:
    """
    Fetch all accessible exercises.
    """
    query = db.query(db_models.Exercise)
    if id is not None:
        query = query.where(db_models.Exercise.id == id)
    if name is not None:
        query = query.where(db_models.Exercise.name == name)
    if owner_user_id is not None:
        query = query.where(db_models.Exercise.owner_user_id == owner_user_id)
    print(query)
    all_exes: list[db_models.Exercise] = query.all()

    #############
    # Permisions
    #############
    # Only return records that are owned by this user or "public", meaning their owner
    # field is null.
    def is_public_or_theirs(ex: db_models.Exercise) -> bool:
        return ex.owner_user_id is None or ex.owner_user_id == current_user.id

    accessible_exes = (ex for ex in all_exes if is_public_or_theirs(ex))

    records = [ExerciseInDB.from_orm(row) for row in accessible_exes]
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
