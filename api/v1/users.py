from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .models.user import UserIn, UserOut
from ..db import models as db_models
from ..db import get_db

router = APIRouter(prefix="/users")


@router.get("/")
def users() -> str:
    return "jk you cannot list all the users, obviously"


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserIn, db: Session = Depends(get_db)) -> UserOut:
    email = user.email
    password = user.password
    hashed_pw = hash_password(password)

    user_record = db_models.User(email=email, pw_hash=hashed_pw)
    db.add(user_record)
    db.commit()
    db.refresh(user_record)
    return user_record
