"""LLM integration for 'Analyze My Workout'.

Provider-agnostic: a small `LLMClient` protocol with two implementations —
`GroqLLMClient` (Groq's OpenAI-compatible chat completions) and `StubLLMClient`
(deterministic, offline). The stub is used automatically when no API key is set,
so tests and local dev never make network calls.
"""
import json
from typing import Protocol

import httpx

from app.config import get_settings
from app.llm.prompts import build_workout_analysis_prompt
from app.llm.schemas import WorkoutAnalysisResponse


class LLMError(Exception):
    """Raised when the LLM provider call fails."""


class LLMClient(Protocol):
    async def complete(self, system: str, user: str) -> str:
        ...


class GroqLLMClient:
    """Calls Groq's OpenAI-compatible /chat/completions endpoint via httpx."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float = 60.0):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def complete(self, system: str, user: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions", json=payload, headers=headers
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMError(f"Groq request failed: {exc}") from exc


class StubLLMClient:
    """Deterministic offline client — returns a valid, generic analysis JSON."""

    async def complete(self, system: str, user: str) -> str:
        return json.dumps(
            {
                "analysis": (
                    "This session shows a balanced mix of exercises. Your effort and "
                    "volume are consistent with a productive workout."
                ),
                "suggestions": [
                    "Prioritize progressive overload on your main lifts.",
                    "Keep rest periods consistent to maintain intensity.",
                ],
                "progress_analysis": (
                    "Compared to your history, your training volume is holding steady. "
                    "Aim to gradually increase reps or sets over the coming weeks."
                ),
                "consistency_analysis": (
                    "Maintaining a regular weekly cadence will accelerate results toward "
                    "your stated goal."
                ),
                "future_recommendations": [
                    "Add one extra working set to your primary exercise next session.",
                    "Include a mobility or cardio finisher to support recovery.",
                ],
            }
        )


def get_llm_client() -> LLMClient:
    """Return the configured client — Groq when a key is present, else the stub."""
    settings = get_settings()
    if settings.LLM_API_KEY:
        return GroqLLMClient(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL,
        )
    return StubLLMClient()


def _parse_response(raw: str) -> WorkoutAnalysisResponse:
    """Parse the model's JSON reply, tolerating stray text around the object."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end == -1:
            raise LLMError("LLM response was not valid JSON")
        data = json.loads(raw[start : end + 1])
    return WorkoutAnalysisResponse.model_validate(data)


async def analyze_workout(
    *, profile: dict, current_session: dict, history: dict
) -> WorkoutAnalysisResponse:
    """Build the prompt, call the LLM, and parse a structured analysis."""
    system, user = build_workout_analysis_prompt(
        profile=profile, current_session=current_session, history=history
    )
    raw = await get_llm_client().complete(system, user)
    return _parse_response(raw)
