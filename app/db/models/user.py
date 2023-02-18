from typing import TYPE_CHECKING, NamedTuple
import uuid

from sqlalchemy import Text, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db.database import Base
from app.db.mixins import ModificationTimesMixin


if TYPE_CHECKING:
    from .workout_type import WorkoutType


class User(Base, ModificationTimesMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(Text, unique=True)
    pw_hash: Mapped[str] = mapped_column(Text)

    owned_workout_types: Mapped[list["WorkoutType"]] = relationship(
        "WorkoutType", back_populates="owner"
    )


class UserWithAuth(NamedTuple):
    """'
    A user along with a JWT header. Useful mainly as an abstraction for testing.

    The auth field will usually be something like: {'Authorization': 'Bearer 123abc'}
    """

    user: User
    auth: dict[str, str]
