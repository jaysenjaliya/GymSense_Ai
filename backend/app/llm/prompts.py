"""Prompt templates for workout analysis.

Builds a (system, user) message pair. The user message injects the current session
JSON, a summarized history, and the user's profile. Kept here so prompts are
testable and easy to iterate on independently of the LLM client.
"""
import json

SYSTEM_PROMPT = """\
You are GymSense AI, an expert strength & conditioning coach and data analyst.
You receive a user's fitness profile, the results of their most recent gym session
(auto-detected from wearable sensor data), and a summary of their workout history.

Give concise, motivating, actionable coaching grounded ONLY in the data provided.
Respect the user's stated fitness goal. Do not invent numbers that aren't present.

Respond with a SINGLE JSON object and nothing else, using exactly these keys:
{
  "analysis": "<2-4 sentence analysis of the current session>",
  "suggestions": ["<actionable tip>", "..."],
  "progress_analysis": "<how this session compares to their history>",
  "consistency_analysis": "<assessment of workout frequency/consistency>",
  "future_recommendations": ["<forward-looking recommendation>", "..."]
}
Keep each list to 2-4 short items."""


def build_workout_analysis_prompt(
    *, profile: dict, current_session: dict, history: dict
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the workout analysis call."""
    user_prompt = (
        "USER PROFILE:\n"
        f"{json.dumps(profile, default=str, indent=2)}\n\n"
        "CURRENT SESSION:\n"
        f"{json.dumps(current_session, default=str, indent=2)}\n\n"
        "WORKOUT HISTORY SUMMARY:\n"
        f"{json.dumps(history, default=str, indent=2)}\n\n"
        "Analyze this workout and respond with the JSON object described above."
    )
    return SYSTEM_PROMPT, user_prompt
