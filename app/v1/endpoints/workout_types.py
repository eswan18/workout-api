from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from ..models.workout_type import WorkoutTypeIn, WorkoutTypeInDB
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db, model_id_exists

router = APIRouter(prefix="/workout_types")


@router.get("/", response_model=list[WorkoutTypeInDB])
def workout_types(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[WorkoutTypeInDB]:
    """
    Fetch all accessible workout types.
    """
    query = select(db_models.WorkoutType)

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
        (db_models.WorkoutType.owner == None)  # noqa
        | (db_models.WorkoutType.owner == current_user)
    )

    result = db.scalars(query)

    records = [WorkoutTypeInDB.from_orm(row) for row in result]
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
    workout_type_record.owner_user_id = current_user.id
    db.add(workout_type_record)
    db.commit()
    db.refresh(workout_type_record)
    return workout_type_record
