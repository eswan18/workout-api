from unittest.mock import patch
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException
import pytest

from app.v1 import auth
from app.db import models as db_models

FAKE_USER_DATA = {"email": "wayne@roughs.net", "password": "ranette"}
FAKE_USER = db_models.User(
    email=FAKE_USER_DATA["email"],
    pw_hash=auth.hash_pw(FAKE_USER_DATA["email"], FAKE_USER_DATA["password"]),
)


def fake_get_user_by_email(db: Any, email: str) -> db_models.User:
    if email == FAKE_USER.email:
        return FAKE_USER
    else:
        raise ValueError


@pytest.mark.anyio
async def test_can_get_user_from_valid_jwt():
    jwt = auth.create_access_token(
        {"sub": FAKE_USER_DATA["email"]},
        timedelta(days=1),
    )
    with patch("app.v1.auth.get_user_by_email", wraps=fake_get_user_by_email) as spy:
        fake_db = None
        retrieved_user = await auth.get_current_user(token=jwt, db=fake_db)
        spy.assert_called_once_with(fake_db, email=FAKE_USER_DATA["email"])
        assert retrieved_user is FAKE_USER


@pytest.mark.anyio
async def test_auth_fails_with_expired_jwt():
    jwt = auth.create_access_token(
        {"sub": FAKE_USER_DATA["email"]},
        timedelta(days=1),
    )

    class FakeTime(datetime):
        @classmethod
        def utcnow(cls):
            return datetime.utcnow() + timedelta(days=2)

    with patch("app.v1.auth.get_user_by_email", fake_get_user_by_email):
        with patch("app.v1.auth.datetime", FakeTime):
            fake_db = None
            with pytest.raises(HTTPException):
                await auth.get_current_user(token=jwt, db=fake_db)
