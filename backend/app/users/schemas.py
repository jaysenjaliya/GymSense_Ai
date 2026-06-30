"""Pydantic schemas for user profile."""
from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    # TODO: id, name, email, age, gender, height, weight, fitness_goal
    email: EmailStr


class UserProfileUpdate(BaseModel):
    # TODO: optional fields for partial profile update
    ...
