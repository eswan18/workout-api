from fastapi import APIRouter

router = APIRouter(prefix='/exercises')


@router.get('/')
def exercises():
    return 'pretend these are all the exercises'
