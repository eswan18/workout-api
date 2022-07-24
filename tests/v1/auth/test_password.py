from unittest.mock import patch
from typing import Any

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


def test_pw_hashing():
    """
    A hashed password should check out when compared.
    """
    email = "marasi@elendel.gov"
    pw = "MeLaan"
    hashed = auth.hash_pw(email, pw)
    assert auth.compare_pw_to_hash(email, pw, hashed)


def test_authenticate_user_works_with_good_creds():
    with patch("app.v1.auth.get_user_by_email", wraps=fake_get_user_by_email) as spy:
        fake_db = None
        retrieved_user = auth.authenticate_user(
            FAKE_USER_DATA["email"],
            FAKE_USER_DATA["password"],
            fake_db,
        )
        spy.assert_called_once_with(fake_db, FAKE_USER_DATA["email"])
        assert retrieved_user is FAKE_USER


def test_authenticate_user_fails_with_wrong_password():
    with patch("app.v1.auth.get_user_by_email", wraps=fake_get_user_by_email) as spy:
        fake_db = None
        retrieved_user = auth.authenticate_user(
            FAKE_USER_DATA["email"],
            "marasi",
            fake_db,
        )
        spy.assert_called_once_with(fake_db, FAKE_USER_DATA["email"])
        assert retrieved_user is None
