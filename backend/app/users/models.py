"""Persistence model for the `users` collection (profile + auth fields).

`UserInDB` is the full stored document: all profile fields plus `hashed_password`
and lifecycle timestamps. The Mongo `_id` is mapped to `id` via alias.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.users.schemas import UserBase


class UserInDB(UserBase):
    """Full stored user document (never returned directly to clients)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class _Timestamps(BaseModel):  # kept for potential reuse by other domains
    created_at: datetime
    updated_at: datetime
