from uuid import UUID

from pydantic import BaseModel, Extra


class User(BaseModel):
    email: str


class UserIn(User):
    password: str


class UserOut(User):
    id: UUID

    class Config:
        orm_mode = True
        extra = Extra.forbid


class UserInDB(UserOut):
    hashed_pw: str

    class Config:
        orm_mode = True
