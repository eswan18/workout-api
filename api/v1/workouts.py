from fastapi import APIRouter

router = APIRouter(prefix="/workouts")


@router.get("/")
def workouts():
    return "pretend these are all the workouts"
