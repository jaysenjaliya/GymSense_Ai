"""MongoDB (async Motor) client and index setup.

Exposes a single shared client/db. `init_indexes` is called on app startup to
create indexes that support common queries (user's session history, date ranges).
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[get_settings().MONGO_DB_NAME]


async def init_indexes() -> None:
    """Create indexes for users / sessions / exercise_logs collections."""
    db = get_db()
    await db.users.create_index("email", unique=True)
    # TODO (later phases):
    # await db.sessions.create_index([("user_id", 1), ("created_at", -1)])
    # await db.exercise_logs.create_index([("session_id", 1)])


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
