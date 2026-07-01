"""Tests for the 'Analyze My Workout' LLM endpoint (uses the offline stub)."""
import os

import pytest

from app.config import get_settings
from app.llm import service as llm_service
from app.llm.schemas import WorkoutAnalysisResponse
from tests.conftest import valid_user_payload

FIXTURE = os.path.join(os.path.dirname(__file__), "data", "sample_session.csv")
_HAS_WEIGHTS = os.path.isfile(get_settings().ML_MODEL_PATH)


async def _auth_headers(client, email="coachme@example.com"):
    await client.post("/auth/register", json=valid_user_payload(email=email))
    login = await client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _upload(client, headers):
    with open(FIXTURE, "rb") as f:
        data = f.read()
    return await client.post(
        "/sessions/upload",
        headers=headers,
        files={"file": ("sample_session.csv", data, "text/csv")},
    )


def test_parse_response_tolerates_surrounding_text():
    raw = 'Sure!\n{"analysis":"a","suggestions":[],"progress_analysis":"p",' \
          '"consistency_analysis":"c","future_recommendations":[]} thanks'
    parsed = llm_service._parse_response(raw)
    assert isinstance(parsed, WorkoutAnalysisResponse)
    assert parsed.analysis == "a"


async def test_analyze_requires_auth(client):
    resp = await client.post("/llm/analyze", json={"session_id": "abc"})
    assert resp.status_code == 401


async def test_analyze_missing_session_404(client):
    headers = await _auth_headers(client)
    resp = await client.post(
        "/llm/analyze", headers=headers, json={"session_id": "64b0c0000000000000000000"}
    )
    assert resp.status_code == 404


@pytest.mark.skipif(not _HAS_WEIGHTS, reason="model_weights.pt not present")
async def test_analyze_returns_structured_response(client):
    headers = await _auth_headers(client)
    session = (await _upload(client, headers)).json()

    resp = await client.post(
        "/llm/analyze", headers=headers, json={"session_id": session["id"]}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {
        "analysis", "suggestions", "progress_analysis",
        "consistency_analysis", "future_recommendations",
    }
    assert isinstance(body["suggestions"], list)
    assert body["analysis"]
