from typing import Any, Self

from sqlalchemy.orm import Session


class FilterMixin:
    """Mixing in FilterMixin adds a .filter method."""

    @classmethod
    def filter(
        cls,
        db: Session,
        filters: dict[str, Any],
        ignore_none: bool = True,
    ) -> list[Self]:
        query = db.query(cls)
        for field, value in filters.items():
            if not ignore_none or value is not None:
                query = query.filter_by(**{field: value})
        return query.all()
