"""Auth routes: register, login, token refresh, and current-user profile."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import service as auth_service
from app.auth.schemas import LoginRequest, RefreshRequest, Token
from app.auth.security import (
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.dependencies import get_current_user
from app.users import service as users_service
from app.users.schemas import UserCreate, UserPublic

router = APIRouter()


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: UserCreate) -> UserPublic:
    try:
        return await auth_service.register_user(payload)
    except users_service.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest) -> Token:
    user = await auth_service.authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest) -> Token:
    try:
        claims = decode_token(payload.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    subject = claims["sub"]
    return Token(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )


@router.get("/me", response_model=UserPublic)
async def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return current_user
