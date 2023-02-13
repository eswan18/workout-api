from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime


class ModificationTimesMixin:
    """
    Mixin for standard created_at, updated_at, deleted_at columns.
    """

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True))
