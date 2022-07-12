import os
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_URL = os.environ["DATABASE_URL"]
db_url = DB_URL.replace('postgres://', 'postgresql://')

Base = declarative_base()


@cache
def get_engine() -> Engine:
    return create_engine(db_url)


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
