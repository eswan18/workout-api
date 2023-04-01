import uuid
from typing import Iterable, cast

from sqlalchemy.sql import Select, column, values, literal, select
from sqlalchemy.types import UUID

from .user import User
from app.db import Base


def missing_references_to_model_query(
    ids: Iterable[uuid.UUID],
    user: User,
    model: type[Base],
) -> Select[tuple[uuid.UUID, str]]:
    """Build a query for IDs that aren't visible to this user, by resource."""
    ids_as_records = [(id,) for id in ids]

    if len(ids_as_records) == 0:
        # This query always returns 0 rows, but it has the right schema.
        return select(
            model.id.label("ref_id"),
            literal(model.__name__).label("ref_type"),
        ).where(False)

    id_values = values(column("id", UUID), name="record_ids").data(ids_as_records)
    # Find which IDs don't match up to a resource that's visible to this user.
    query: Select[tuple[uuid.UUID, str]] = (
        select(  # type: ignore
            column("id").label("ref_id"),
            literal(model.__name__).label("ref_type"),
        )
        .select_from(id_values)
        .where(
            column("id").not_in(
                # This line relies on the model class having some features that all the
                # "standard" models do: a `id` column, and a `readable_by` method.
                select(model.id).where(model.readable_by(user=user))  # type: ignore [attr-defined]
            )
        )
    )
    return cast(Select[tuple[uuid.UUID, str]], query)
