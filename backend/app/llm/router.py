"""LLM routes: "Analyze My Workout" — AI recommendations from session + history."""
from fastapi import APIRouter

router = APIRouter()

# TODO: POST /analyze -> send current session + history summary + profile to LLM,
#                        return analysis, suggestions, progress/consistency, future recs
