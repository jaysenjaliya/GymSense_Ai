"""Pydantic schemas for LLM analysis requests/responses."""
from pydantic import BaseModel


class WorkoutAnalysisResponse(BaseModel):
    # TODO: analysis, suggestions, progress_analysis, consistency_analysis,
    #       future_recommendations
    ...
