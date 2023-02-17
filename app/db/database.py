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
    return create_engine(db_url, echo=True)


async def get_session() -> AsyncIterator[Session]:
    engine = get_engine()
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=True,
        bind=engine,
    )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_session_factory() -> AsyncIterator[sessionmaker[Session]]:
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    yield session_factory