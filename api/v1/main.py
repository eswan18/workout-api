from fastapi import APIRouter

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


router.include_router(exercises.router)
router.include_router(users.router)
router.include_router(sets.router)
router.include_router(workouts.router)
router.include_router(workout_types.router)
