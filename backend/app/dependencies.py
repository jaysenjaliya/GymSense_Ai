"""Shared FastAPI dependencies (auth guards, current-user resolution)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import ACCESS_TOKEN_TYPE, TokenError, decode_token
from app.users import service as users_service
from app.users.schemas import UserPublic

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    """Resolve the authenticated user from a Bearer access token.

    Raises 401 on a missing/invalid/expired token or if the user no longer exists.
    """
    try:
        claims = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    except TokenError:
        raise _credentials_exception

    user = await users_service.get_user_by_id(claims["sub"])
    if user is None:
        raise _credentials_exception

    return UserPublic.model_validate(user, from_attributes=True)
