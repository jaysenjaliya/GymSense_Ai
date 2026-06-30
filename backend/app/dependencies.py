"""Shared FastAPI dependencies (auth guards, current-user resolution)."""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Resolve the authenticated user from a JWT access token."""
    # TODO: decode token (app.auth.security), load user from db, raise 401 on failure
    ...
