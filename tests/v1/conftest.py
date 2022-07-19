from uuid import UUID
from typing import Iterator

from fastapi.testclient import TestClient
import pytest

from app.v1 import app, auth
from app.db import models as db_models


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="function")
def fake_current_user(client) -> Iterator[db_models.User]:
    user = db_models.User(
        id=UUID("117e87dd-9f1a-4f20-a4c1-4fa646077370"),  # type: ignore
        email="elend@elendel.gov",
        pw_hash="16161616",
    )

    async def get_fake_user() -> db_models.User:
        return user

    client.app.dependency_overrides[auth.get_current_user] = get_fake_user
    yield user
    del client.app.dependency_overrides[auth.get_current_user]
