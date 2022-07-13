from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    email: str


class UserIn(User):
    password: str


class UserOut(User):
    id: UUID


class UserInDB(UserOut):
    hashed_pw: str

    class Config:
        orm_mode = True
