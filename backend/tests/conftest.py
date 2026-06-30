"""Shared pytest fixtures (test client, mock db, sample sensor data)."""
import pytest


@pytest.fixture
def client():
    """FastAPI TestClient/httpx AsyncClient fixture."""
    # TODO: build app via create_app() with overridden dependencies
    ...
