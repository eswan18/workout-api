import os
from uuid import UUID
from functools import cache
from typing import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session


DB_URL = os.environ["DATABASE_URL"]
db_url = DB_URL.replace("postgres://", "postgresql://")


class Base(DeclarativeBase):
    pass


@cache
def get_engine() -> Engine:
    return create_engine(db_url)


async def get_db() -> AsyncIterator[Session]:
    engine = get_engine()
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def model_id_exists(
    Model: type[Base],
    id: str | UUID,
    db: Session,
) -> bool:
    """
    Check whether an ID exists for a particular model in the DB.
    """
    first_instance = db.query(Model.id).filter_by(id=id).first()  # type: ignore
    if first_instance is None:
        return False
    else:
        return True
