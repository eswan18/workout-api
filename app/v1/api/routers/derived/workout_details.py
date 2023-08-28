from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session

from app import db
from app.db.views import get_v_workout_by_workout_id, get_v_exercises_by_workout_id
from app.v1.models.workout_details import WorkoutDetails
from app.v1.auth import get_current_user


router = APIRouter(prefix="/derived/workout_details")


@router.get("/{id}", response_model=WorkoutDetails)
def read_workout_details(
    id: UUID,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> WorkoutDetails:
    with session_factory() as session:
        workout = get_v_workout_by_workout_id(
            current_user=current_user, workout_id=id, session=session
        )
        if workout is None:
            raise HTTPException(status_code=404, detail="Workout not found")
        exercises = get_v_exercises_by_workout_id(
            current_user=current_user, workout_id=id, session=session
        )
    return WorkoutDetails(workout=workout, exercises=exercises)
