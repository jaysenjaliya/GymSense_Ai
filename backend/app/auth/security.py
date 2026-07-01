"""Password hashing (passlib/bcrypt) and JWT encode/decode (python-jose).

A single `JWT_SECRET_KEY` signs both token kinds; they are distinguished by a
`type` claim (`access` / `refresh`) so a refresh token can't be used as an access
token and vice-versa.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    claims = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject,
        ACCESS_TOKEN_TYPE,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject,
        REFRESH_TOKEN_TYPE,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


class TokenError(Exception):
    """Raised when a token is invalid, expired, or of the wrong type."""


def decode_token(token: str, *, expected_type: str) -> dict:
    """Decode and validate a JWT, enforcing its `type` claim. Returns the claims."""
    settings = get_settings()
    try:
        claims = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as exc:
        raise TokenError("Could not validate token") from exc

    if claims.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token")
    if not claims.get("sub"):
        raise TokenError("Token missing subject")
    return claims
