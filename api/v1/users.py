from fastapi import APIRouter

router = APIRouter(prefix='/users')


@router.get('/')
def users():
    return 'pretend these are all the users'
