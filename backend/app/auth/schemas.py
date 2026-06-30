"""Pydantic schemas for auth requests/responses."""
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    # TODO: name, email, password, age, gender, height, weight, fitness_goal
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
