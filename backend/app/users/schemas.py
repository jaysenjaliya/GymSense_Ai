"""Pydantic schemas for the user data lifecycle.

Three distinct shapes:
- `UserCreate`  : registration input (raw password).
- `UserInDB`    : persisted document (see models.py — hashed_password, timestamps).
- `UserPublic`  : API output (never exposes the password).

Units are encoded in field names (`height_cm`, `weight_kg`) and the `fitness_goal`
enum is locked to three values because downstream calorie math and LLM prompts
depend on them.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class FitnessGoal(str, Enum):
    fat_loss = "fat_loss"
    hypertrophy = "hypertrophy"
    endurance = "endurance"


class UserBase(BaseModel):
    """Profile fields shared across create/output schemas."""

    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    age: int = Field(..., gt=0, lt=120)
    gender: Gender
    height_cm: float = Field(..., gt=0, description="Height in centimeters")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    fitness_goal: FitnessGoal


class UserCreate(UserBase):
    """Registration input — carries the raw password."""

    password: str = Field(..., min_length=8, max_length=128)


class UserPublic(UserBase):
    """Public-facing user profile. Excludes the hashed password by construction."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(..., alias="id")
    created_at: datetime
    updated_at: datetime
