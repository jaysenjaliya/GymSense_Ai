"""Pydantic schemas for analytics responses."""
from pydantic import BaseModel


class UserAnalyticsSummary(BaseModel):
    # TODO: totals, per-exercise breakdown, trends over time
    ...
