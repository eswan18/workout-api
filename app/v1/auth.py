import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.sql import select
from sqlalchemy.orm import Session, sessionmaker

from app import db


APP_SECRET = os.environ["APP_SECRET"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION_MINUTES = 60 * 24  # One day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(session_factory: sessionmaker[Session], email: str) -> db.User:
    query = select(db.User).filter_by(email=email)
    with session_factory() as session:
        user = session.scalars(query).one()
    if user is None:
        raise ValueError(f"User with email '{email}' does not exist")
    return user


def compare_pw_to_hash(email: str, plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(email.lower() + plain_password, hashed_password)


def hash_pw(email: str, password: str) -> str:
    return pwd_context.hash(email.lower() + password)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
) -> db.User:
    """
    Return the user model of the owner of an access token. Raise exception if invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        if "sub" not in payload:
            raise credentials_exception
        if "exp" not in payload:
            raise credentials_exception
        user_email: str = payload["sub"]
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    expire_time = datetime.fromtimestamp(float(payload["exp"]))
    if datetime.utcnow() >= expire_time:
        raise credentials_exception

    user = get_user_by_email(session_factory, email=user_email)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(
    email: str,
    password: str,
    session_factory: sessionmaker[Session] = Depends(db.get_session_factory),
) -> db.User | None:
    """
    Given an email & password, return a user if the login is valid; otherwise None.
    """
    # Find the user for this email
    try:
        user = get_user_by_email(session_factory, email)
    except ValueError:
        return None
    # Confirm the password is correct.
    is_correct_pw = compare_pw_to_hash(email, password, user.pw_hash)
    if is_correct_pw:
        return user
    else:
        return None


def generate_jwt(
    email: str,
    expiration_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES),
) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": email}, expiration_delta=expiration_delta
    )
    return {"access_token": access_token, "token_type": "bearer"}


def create_access_token(
    data: dict[str, str],
    expiration_delta: timedelta,
) -> str:
    """
    Create a jwt for a user, with specified time-to-live.
    """
    expire_time = datetime.utcnow() + expiration_delta
    expire_time_numeric = int(expire_time.timestamp())
    to_encode = data | {"exp": expire_time_numeric}
    encoded_jwt = jwt.encode(to_encode, APP_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str) -> dict[str, str]:
    """
    Decode a jwt for a user, with specified time-to-live.
    """
    payload = jwt.decode(token, APP_SECRET, algorithms=[ALGORITHM])
    return payload
