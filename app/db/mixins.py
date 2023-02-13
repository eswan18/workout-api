from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class ModificationTimesMixin:
    """
    Mixin for standard created_at, updated_at, deleted_at columns.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
