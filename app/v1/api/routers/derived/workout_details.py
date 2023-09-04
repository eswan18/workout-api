from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import sessionmaker, Session

from app import db
from app.db.views import (
    get_v_workout_by_workout_id,
    get_v_workouts_sorted,
    get_v_exercises_by_workout_id,
)
from app.v1.models.workout_details import WorkoutDetails
from app.v1.auth import get_current_user


router = APIRouter(prefix="/derived/workout_details")


@router.get("/", response_model=list[WorkoutDetails])
def read_workout_details(
    id: UUID | None = Query(default=None),
    limit: int = 10,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
    current_user: db.User = Depends(get_current_user),
) -> list[WorkoutDetails]:
    with session_factory() as session:
        if id is not None:
            workout = get_v_workout_by_workout_id(
                current_user=current_user, workout_id=id, session=session
            )
            if workout is None:
                # We should explicity give a 404 if the user asked for a specific workout.
                raise HTTPException(status_code=404, detail="Workout not found")
            else:
                workouts = [workout]
        else:
            workouts = get_v_workouts_sorted(
                current_user=current_user,
                session=session,
                order_by="start_time",
                asc=False,
                limit=limit,
            )

    wktDetails: list[WorkoutDetails] = []
    for workout in workouts:
        exercises = get_v_exercises_by_workout_id(
            current_user=current_user, workout_id=workout.id, session=session
        )
        wktDetails.append(WorkoutDetails(workout=workout, exercises=exercises))

    return wktDetails
