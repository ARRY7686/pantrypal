import os

# Point the app at a throwaway SQLite file BEFORE it is imported, so tests never touch PostgreSQL.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:  # the context manager runs the lifespan (create_all)
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def make_item(client):
    def _make(**overrides):
        payload = {"name": "Milk", "category": "dairy", "location": "fridge", "quantity": 1, "unit": "l"}
        payload.update(overrides)
        response = client.post("/api/items", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make
