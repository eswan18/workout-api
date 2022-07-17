from fastapi import FastAPI

from . import token
from . import exercises
from . import users
from . import sets
from . import workouts
from . import workout_types

v1_app = FastAPI()


@v1_app.get("/")
def home():
    return "you've reached v1 of the api"


v1_app.include_router(token.router, tags=["Login"])
v1_app.include_router(users.router, tags=["Users"])
v1_app.include_router(exercises.router, tags=["Exercises"])
v1_app.include_router(sets.router, tags=["Sets"])
v1_app.include_router(workouts.router, tags=["Workouts"])
v1_app.include_router(workout_types.router, tags=["Workout Types"])
