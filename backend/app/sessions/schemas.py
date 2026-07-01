"""Pydantic schemas for session upload results and listings."""
from datetime import datetime

from pydantic import BaseModel


class ExerciseResult(BaseModel):
    """Per-exercise breakdown within a session."""

    exercise: str
    sets: int
    reps: int
    duration_seconds: float
    estimated_calories: float


class SessionResult(BaseModel):
    """Full result of a processed session (returned by upload and get-by-id)."""

    id: str
    created_at: datetime
    filename: str | None = None
    total_duration_seconds: float
    active_duration_seconds: float
    total_reps: int
    total_estimated_calories: float
    exercises: list[ExerciseResult]
    summary: str


class SessionSummary(BaseModel):
    """Lightweight item for history listings."""

    id: str
    created_at: datetime
    total_duration_seconds: float
    exercise_count: int
    total_reps: int
    total_estimated_calories: float
