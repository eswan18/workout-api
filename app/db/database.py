import os
from uuid import UUID
from functools import cache
from typing import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session, DeclarativeMeta


DB_URL = os.environ["DATABASE_URL"]
db_url = DB_URL.replace("postgres://", "postgresql://")

Base = declarative_base()


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
    Model: DeclarativeMeta,
    id: str | UUID,
    db: Session,
) -> bool:
    first_instance = db.query(Model.id).filter_by(id=id).first()  # type: ignore
    if first_instance is None:
        return False
    else:
        return True
