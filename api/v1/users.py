from fastapi import APIRouter

router = APIRouter(prefix="/users")


@router.get("/")
def users() -> str:
    return "jk you cannot list all the users, obviously"
