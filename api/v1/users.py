from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models.user import UserIn, UserOut
from ..db import models as db_models
from ..db import get_db
from .auth import hash_pw

router = APIRouter(prefix="/users")


@router.get("/")
def users() -> str:
    return "jk you cannot list all the users, obviously"


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserIn, db: Session = Depends(get_db)) -> UserOut:
    email = user.email
    password = user.password
    hashed_pw = hash_pw(email, password)

    user_record = db_models.User(email=email, pw_hash=hashed_pw)
    try:
        db.add(user_record)
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="an account with that email address is already in use",
        )
    db.refresh(user_record)
    return user_record
