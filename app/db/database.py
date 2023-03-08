import os
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
def get_engine(echo: bool = True) -> Engine:
    return create_engine(db_url, echo=echo)


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


async def get_session_factory(echo: bool = True) -> AsyncIterator[sessionmaker[Session]]:
    engine = get_engine(echo=echo)
    session_factory = sessionmaker(bind=engine)
    yield session_factory


def get_session_factory_sync(echo: bool = True) -> sessionmaker[Session]:
    engine = get_engine(echo=echo)
    session_factory = sessionmaker(bind=engine)
    return session_factory
