"""Persistence document shapes for `sessions` and `exercise_logs` collections.

- `sessions`      : one doc per upload — metadata + aggregate analytics + the
                    embedded per-exercise breakdown (denormalized for fast reads).
- `exercise_logs` : one doc per exercise per session — used by cross-session
                    analytics aggregation (Phase 4).

The service layer writes/reads plain dicts; these models document the schema and
can be used for validation.
"""
from datetime import datetime

from pydantic import BaseModel

from app.sessions.schemas import ExerciseResult


class SessionInDB(BaseModel):
    id: str | None = None          # str(_id)
    user_id: str
    filename: str | None = None
    created_at: datetime
    total_duration_seconds: float
    active_duration_seconds: float
    total_reps: int
    total_estimated_calories: float
    n_windows: int
    summary: str
    exercises: list[ExerciseResult]


class ExerciseLogInDB(BaseModel):
    id: str | None = None
    session_id: str
    user_id: str
    created_at: datetime
    exercise: str
    sets: int
    reps: int
    duration_seconds: float
    estimated_calories: float
