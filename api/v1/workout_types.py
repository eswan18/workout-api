from fastapi import APIRouter

router = APIRouter(prefix='/workout_types')


@router.get('/')
def workout_types():
    return 'pretend these are all the workout types'
