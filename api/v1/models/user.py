from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str


class UserIn(User):
    password: str


class UserInDB(User):
    id: str
    hashed_pw: str


class UserOut(User):
    id: str
