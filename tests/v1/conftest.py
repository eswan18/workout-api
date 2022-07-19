from fastapi.testclient import TestClient
import pytest

from app.v1 import app

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
