import os
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_URL = os.environ["DATABASE_URL"]

Base = declarative_base()


@cache
def get_engine() -> Engine:
    return create_engine(DB_URL)


async def get_db():
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
