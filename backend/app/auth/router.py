"""Auth routes: register, login, token refresh."""
from fastapi import APIRouter

router = APIRouter()

# TODO: POST /register  -> create user, return tokens
# TODO: POST /login     -> verify credentials, return access + refresh tokens
# TODO: POST /refresh   -> issue new access token from a valid refresh token
