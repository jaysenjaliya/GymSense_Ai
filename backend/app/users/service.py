"""User repository: async CRUD against the `users` collection.

Returns `UserInDB` models (with stringified `_id`) so callers never touch raw
Mongo documents. `create_user` surfaces duplicate-email collisions as a custom
exception so the auth layer can map it to HTTP 409.
"""
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from app.database import get_db
from app.users.models import UserInDB


class EmailAlreadyExistsError(Exception):
    """Raised when inserting a user whose email already exists."""


def _to_model(doc: dict | None) -> UserInDB | None:
    if doc is None:
        return None
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    return UserInDB.model_validate(doc)


async def create_user(doc: dict) -> UserInDB:
    """Insert a user document. `doc` must NOT contain `_id`."""
    try:
        result = await get_db().users.insert_one(doc)
    except DuplicateKeyError as exc:
        raise EmailAlreadyExistsError(doc.get("email", "")) from exc
    created = {**doc, "_id": result.inserted_id}
    return _to_model(created)  # type: ignore[return-value]


async def get_user_by_email(email: str) -> UserInDB | None:
    doc = await get_db().users.find_one({"email": email})
    return _to_model(doc)


async def get_user_by_id(user_id: str) -> UserInDB | None:
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    doc = await get_db().users.find_one({"_id": oid})
    return _to_model(doc)
