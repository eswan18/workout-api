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

    # Filters
    eq_filters = {"id": id, "name": name, "owner_user_id": owner_user_id}
    # Ignore any that weren't provided.
    eq_filters = {
        key: value for (key, value) in eq_filters.items() if value is not None
    }
    query = query.filter_by(**eq_filters)

    # Permisions
    # Only return records that are owned by this user or "public", meaning their owner
    # field is null.
    query = query.filter(
        (db_models.Exercise.owner == None)  # noqa
        | (db_models.Exercise.owner == current_user)
    )

    results = query.all()

    records = [ExerciseInDB.from_orm(row) for row in results]
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
