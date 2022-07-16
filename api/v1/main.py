from fastapi import APIRouter

from . import token
from . import exercises
from . import users
from . import sets
from . import workouts
from . import workout_types

router = APIRouter(
    prefix="/v1",
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def v1_home():
    return "you've reached v1 of the api"


router.include_router(token.router, tags=['Login'])
router.include_router(users.router, tags=['Users'])
router.include_router(exercises.router, tags=['Exercises'])
router.include_router(sets.router, tags=['Sets'])
router.include_router(workouts.router, tags=['Workouts'])
router.include_router(workout_types.router, tags=['Workout Types'])
