from string import ascii_letters
from random import choices
from uuid import UUID, uuid4
from typing import Iterator

from fastapi.testclient import TestClient
import pytest

from app.v1 import app, auth
from app import db
from app.db.database import get_session_factory_sync
from app.v1.auth import hash_pw, generate_jwt


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="function")
def fake_current_user(client) -> Iterator[db.User]:
    user = db.User(
        id=UUID("117e87dd-9f1a-4f20-a4c1-4fa646077370"),  # type: ignore
        email="elend@elendel.gov",
        pw_hash="16161616",
    )

    async def get_fake_user() -> db.User:
        return user

    client.app.dependency_overrides[auth.get_current_user] = get_fake_user
    yield user
    del client.app.dependency_overrides[auth.get_current_user]


@pytest.fixture(scope="session", autouse=True)
def test_user_account() -> db.User:
    # Create a unique, fake user.
    user_string = "".join(choices(ascii_letters, k=15))
    password = "".join(choices(ascii_letters, k=15))
    unique_email = f"testuser-{user_string}@example.com"
    pw_hash = hash_pw(unique_email, password)
    user = db.User(
        id=uuid4(),
        email=unique_email,
        pw_hash=pw_hash,
    )
    # Insert it in the db.
    session_factory = get_session_factory_sync()
    with session_factory(expire_on_commit=False) as session:
        session.add(user)
        session.commit()
    return user


@pytest.fixture
def test_user_auth(test_user_account: db.User) -> dict[str, str]:
    jwt = generate_jwt(test_user_account.email)
    auth_header = {"Authorization": f"Bearer {jwt['access_token']}"}
    return auth_header
