"""Pydantic schemas for LLM analysis requests/responses."""
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Which stored session to analyze (history + profile are pulled server-side)."""

    session_id: str


class WorkoutAnalysisResponse(BaseModel):
    """Structured 'Analyze My Workout' output returned to the client."""

    analysis: str = Field(..., description="Overall analysis of the current session")
    suggestions: list[str] = Field(default_factory=list)
    progress_analysis: str = Field(..., description="Progress vs. past sessions")
    consistency_analysis: str = Field(..., description="Workout frequency / consistency")
    future_recommendations: list[str] = Field(default_factory=list)
