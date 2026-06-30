"""Password hashing (passlib/bcrypt) and JWT encode/decode (python-jose)."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    """Encode a short-lived access token."""
    # TODO: jwt.encode with JWT_SECRET_KEY + ACCESS_TOKEN_EXPIRE_MINUTES
    ...


def create_refresh_token(subject: str) -> str:
    """Encode a long-lived refresh token."""
    # TODO: jwt.encode with JWT_REFRESH_SECRET_KEY + REFRESH_TOKEN_EXPIRE_DAYS
    ...


def decode_token(token: str, *, refresh: bool = False) -> dict:
    """Decode and validate a JWT, returning its claims."""
    # TODO: jwt.decode; raise on expiry/invalid signature
    ...
