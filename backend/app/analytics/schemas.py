"""Pydantic schemas for analytics responses."""
from datetime import datetime

from pydantic import BaseModel


class ExerciseAggregate(BaseModel):
    """Cross-session totals for a single exercise."""

    exercise: str
    sessions_count: int
    total_sets: int
    total_reps: int
    total_duration_seconds: float
    total_estimated_calories: float


class UserAnalyticsSummary(BaseModel):
    """Aggregate view across a user's entire workout history (dashboard)."""

    total_sessions: int
    total_active_seconds: float
    total_reps: int
    total_estimated_calories: float
    first_session_at: datetime | None = None
    last_session_at: datetime | None = None
    sessions_last_7_days: int
    favorite_exercise: str | None = None
    per_exercise: list[ExerciseAggregate]
