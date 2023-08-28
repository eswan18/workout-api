from pydantic import BaseModel
from app.db.views import VWorkout, VExercise


class WorkoutDetails(BaseModel):
    workout: VWorkout
    exercises: list[VExercise]
