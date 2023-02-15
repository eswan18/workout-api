from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from ..models.workout import WorkoutIn, WorkoutInDB
from ..auth import get_current_user
from ...db import models as db_models
from ...db import get_db, model_id_exists

router = APIRouter(prefix="/workouts")


@router.get("/", response_model=list[WorkoutInDB])
def workouts(
    id: UUID | None = None,
    status: str | None = None,
    workout_type_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> list[WorkoutInDB]:
    """
    Fetch all the workouts for your user.

    Not yet implemented: filtering by workout time. That'll be tricky since it needs to
    support gt/lt, not just equality.
    """
    query = select(db_models.Workout)

    # Filters
    eq_filters = {"id": id, "status": status, "workout_type_id": workout_type_id}
    # Ignore any that weren't provided.
    eq_filters = {
        key: value for (key, value) in eq_filters.items() if value is not None
    }
    query = query.filter_by(**eq_filters)

    # Permissions
    query = query.filter_by(user=current_user)

    result = db.scalars(query)
    records = [WorkoutInDB.from_orm(row) for row in result]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WorkoutInDB)
def create_workout(
    workout: WorkoutIn,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
) -> db_models.Workout:
    """
    Record a new workout.
    """
    # Add the current user's ID to the record.
    workout_dict = workout.dict()
    workout_dict["user_id"] = current_user.id

    # Validate that the workout_type_id, if included, is present in the DB.
    workout_type_id = workout_dict["workout_type_id"]
    if workout_type_id is not None:
        if not model_id_exists(Model=db_models.WorkoutType, id=workout_type_id, db=db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"workout type with id {workout_type_id} does not exist",
            )

    workout_record = db_models.Workout(**workout_dict)
    db.add(workout_record)
    db.commit()
    db.refresh(workout_record)
    return workout_record
