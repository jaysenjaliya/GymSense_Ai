"""Auth business logic: registration and credential verification."""
from datetime import datetime, timezone

from app.auth.security import hash_password, verify_password
from app.users import service as users_service
from app.users.models import UserInDB
from app.users.schemas import UserCreate, UserPublic


async def register_user(payload: UserCreate) -> UserPublic:
    """Hash the password, persist the user, and return the public profile.

    Raises `users_service.EmailAlreadyExistsError` on a duplicate email.
    """
    now = datetime.now(timezone.utc)
    doc = payload.model_dump(mode="json", exclude={"password"})
    doc["hashed_password"] = hash_password(payload.password)
    doc["created_at"] = now
    doc["updated_at"] = now

    user = await users_service.create_user(doc)
    return UserPublic.model_validate(user, from_attributes=True)


async def authenticate_user(email: str, password: str) -> UserInDB | None:
    """Return the user if the email exists and the password matches, else None."""
    user = await users_service.get_user_by_email(email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
