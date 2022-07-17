from fastapi import APIRouter

router = APIRouter(prefix="/sets")


@router.get("/")
def sets():
    return "pretend these are all the sets"
