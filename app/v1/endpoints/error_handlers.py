from typing import Literal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from psycopg2.errors import ForeignKeyViolation
from fastapi import HTTPException


class handle_db_errors:
    """
    Run database-related code with error handling and automatic rollback.

    Known errors are converted to an HTTPException and reraised. The db session is rolled back as soon as an error occurs.
    """

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        pass

    def __exit__(
        self, exc_type: type[Exception], exc_value: Exception, traceback
    ) -> Literal[False]:
        """
        Handle errors and close the context.
        """
        if exc_type is not None:
            # Roll back the session and try to convert errors to HTTPExceptions.
            self.session.rollback()
            http_exc = self._error_to_http_exception(exc_value)
            if http_exc is not None:
                raise http_exc
            else:
                return False

    def _error_to_http_exception(self, exc_value: Exception) -> HTTPException | None:
        """
        Convert known categories of errors into HTTPExceptions.
        """
        self.session.rollback()

        if isinstance(exc_value, IntegrityError):
            original_error = exc_value.orig
            if isinstance(original_error, ForeignKeyViolation):
                msg = str(original_error)
            else:
                msg = str(exc_value.detail)
            return HTTPException(status_code=400, detail=msg)

        return None