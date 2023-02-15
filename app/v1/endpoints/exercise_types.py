from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from app.v1.models.exercise_type import ExerciseTypeInDB, ExerciseTypeIn
from app.v1.auth import get_current_user
from app import db

router = APIRouter(prefix="/exercise_types")


@router.get("/", response_model=list[ExerciseTypeInDB])
def exercise_types(
    id: UUID | None = None,
    name: str | None = None,
    owner_user_id: UUID | None = None,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> list[ExerciseTypeInDB]:
    """
    Fetch all accessible exercise types.
    """
    param_filter = db.ExerciseType.param_filter(
        id=id, name=name, owner_user_id=owner_user_id
    )
    readable_filter = db.ExerciseType.read_permissions_filter(current_user)
    query = select(db.ExerciseType).where(param_filter & readable_filter)

    result = session.scalars(query)
    records = [ExerciseTypeInDB.from_orm(ex_tp) for ex_tp in result]
    return records


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ExerciseTypeInDB)
def create_exercise(
    exercise_type: ExerciseTypeIn,
    session: Session = Depends(db.get_db),
    current_user: db.User = Depends(get_current_user),
) -> db.ExerciseType:
    """
    Create a new exercise type.
    """
    exercise_type_record = db.ExerciseType(**exercise_type.dict())
    exercise_type_record.owner_user_id = current_user.id
    session.add(exercise_type_record)
    session.commit()
    session.refresh(exercise_type_record)
    return exercise_type_record
