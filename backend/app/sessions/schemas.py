"""Pydantic schemas for session upload results and listings."""
from pydantic import BaseModel


class ExerciseResult(BaseModel):
    # TODO: exercise, sets, reps, duration_seconds, est_calories
    ...


class SessionResult(BaseModel):
    # TODO: total_duration, exercises: list[ExerciseResult], summary, created_at
    ...


class SessionSummary(BaseModel):
    # TODO: lightweight item for history listings
    ...
