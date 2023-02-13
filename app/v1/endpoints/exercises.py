from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..models.exercise_type import ExerciseTypeInDB, ExerciseTypeIn
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db

router = APIRouter(prefix="/exercises_types")


@router.get("/", response_model=list[ExerciseTypeInDB])
def exercises_types(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[ExerciseTypeInDB]:
    """
    Fetch all accessible exercises.
    """
    query = db.query(db_models.ExerciseType)

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
        (db_models.ExerciseType.owner == None)  # noqa
        | (db_models.ExerciseType.owner == current_user)
    )

    results = query.all()

    records = [ExerciseTypeInDB.from_orm(row) for row in results]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ExerciseTypeInDB)
def create_exercise(
    exercise: ExerciseTypeIn,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> db_models.ExerciseType:
    """
    Create a new exercise.
    """
    exercise_record = db_models.ExerciseType(**exercise.dict())
    exercise_record.owner_user_id = current_user.id
    db.add(exercise_record)
    db.commit()
    db.refresh(exercise_record)
    return exercise_record
