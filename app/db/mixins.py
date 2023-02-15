from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import Mapped, mapped_column


# From https://stackoverflow.com/questions/15424199/howto-current-timestamp-at-time-zone-utc  # noqa
current_timestamp_utc = func.timezone("UTC", func.current_timestamp())


class ModificationTimesMixin:
    """
    Mixin for standard created_at, updated_at, deleted_at columns.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=current_timestamp_utc,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=current_timestamp_utc,
        onupdate=current_timestamp_utc,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
