from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from ..models.workout_type import WorkoutTypeIn, WorkoutTypeInDB
from ..auth import get_current_user
from app import db

router = APIRouter(prefix="/workout_types")


@router.get("/", response_model=list[WorkoutTypeInDB])
def workout_types(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> list[WorkoutTypeInDB]:
    """
    Fetch all accessible workout types.
    """
    query = select(db.WorkoutType)
    query = db.WorkoutType.apply_params(
        query=query, id=id, name=name, owner_user_id=owner_user_id
    )
    query = db.WorkoutType.apply_read_permissions(query, current_user)

    result = session.scalars(query)
    records = [WorkoutTypeInDB.from_orm(row) for row in result]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WorkoutTypeInDB)
def create_workout_type(
    workout_type: WorkoutTypeIn,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> db.WorkoutType:
    """
    Create a new workout type.
    """
    # Make sure that the parent workout type ID, if included, is in the DB.
    parent_id = workout_type.parent_workout_type_id
    if parent_id is not None:
        if not db.model_id_exists(Model=db.WorkoutType, id=parent_id, session=session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"workout type with id {parent_id} does not exist",
            )

    workout_type_record = db.WorkoutType(**workout_type.dict())
    workout_type_record.owner_user_id = current_user.id
    session.add(workout_type_record)
    session.commit()
    session.refresh(workout_type_record)
    return workout_type_record
