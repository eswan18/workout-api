import os

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.v1.models.user import UserIn, UserOut
from app.v1.auth import get_current_user
from app import db
from app.v1.auth import hash_pw
from app.v1.lifecycle import publish_lifeycle_event, Action

USER_CREATION_SECRET = os.environ["USER_CREATION_SECRET"]

router = APIRouter(prefix="/users")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(
    user: UserIn,
    secret: str = Body(),
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
) -> db.User:
    """
    Create a new user. Requires a secret string, for now.
    """
    if secret != USER_CREATION_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user creation secret",
        )

    email = user.email
    password = user.password
    hashed_pw = hash_pw(email, password)

    record = db.User(email=email, pw_hash=hashed_pw)
    with session_factory(expire_on_commit=False) as session:
        session.add(record)
        try:
            session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="an account with that email address is already in use",
            )

    # We have to publish events manually here because this endpoint doesn't require
    # authentication.
    publish_lifeycle_event(
        resource=db.User,
        action=Action.CREATE,
        resource_id=record.id,
        user=email,
    )
    return record


@router.get("/me", response_model=UserOut)
def get_me(
    current_user: db.User = Depends(get_current_user),
) -> db.User:
    """
    Fetch information about your own user.
    """
    return current_user
