"""Shared pytest fixtures.

The `client` fixture runs the real FastAPI app against an in-memory MongoDB
(`mongomock-motor`) so auth tests need no live database. If mongomock-motor is
not installed, the auth tests skip cleanly.
"""
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def client(monkeypatch):
    import pytest

    try:
        from mongomock_motor import AsyncMongoMockClient
    except ImportError:  # pragma: no cover
        pytest.skip("mongomock-motor not installed and no test Mongo configured")

    import app.database as database
    from app.config import get_settings

    # Point config at deterministic test values, then bust the lru_cache.
    monkeypatch.setenv("MONGO_DB_NAME", "test_gymsense")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    get_settings.cache_clear()

    # Swap the shared Motor client for an in-memory mock (auto-restored after test).
    monkeypatch.setattr(database, "_client", AsyncMongoMockClient())
    await database.init_indexes()

    from app.main import create_app

    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    get_settings.cache_clear()


def valid_user_payload(**overrides) -> dict:
    """A valid UserCreate body; override individual fields as needed."""
    payload = {
        "name": "Jay Doe",
        "email": "jay@example.com",
        "password": "supersecret123",
        "age": 30,
        "gender": "male",
        "height_cm": 180.0,
        "weight_kg": 75.0,
        "fitness_goal": "hypertrophy",
    }
    payload.update(overrides)
    return payload
