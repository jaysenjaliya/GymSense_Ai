"""Tests for the aggregate analytics summary endpoint."""
import os

import pytest

from app.config import get_settings
from tests.conftest import valid_user_payload

FIXTURE = os.path.join(os.path.dirname(__file__), "data", "sample_session.csv")
_HAS_WEIGHTS = os.path.isfile(get_settings().ML_MODEL_PATH)


async def _auth_headers(client, email="analytics@example.com"):
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


async def test_summary_requires_auth(client):
    assert (await client.get("/analytics/summary")).status_code == 401


async def test_summary_empty_for_new_user(client):
    headers = await _auth_headers(client, email="fresh@example.com")
    resp = await client.get("/analytics/summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_sessions"] == 0
    assert body["total_reps"] == 0
    assert body["sessions_last_7_days"] == 0
    assert body["favorite_exercise"] is None
    assert body["per_exercise"] == []
    assert body["first_session_at"] is None


@pytest.mark.skipif(not _HAS_WEIGHTS, reason="model_weights.pt not present")
async def test_summary_aggregates_across_sessions(client):
    headers = await _auth_headers(client)
    s1 = (await _upload(client, headers)).json()
    s2 = (await _upload(client, headers)).json()

    resp = await client.get("/analytics/summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()

    assert body["total_sessions"] == 2
    assert body["sessions_last_7_days"] == 2
    # Totals equal the sum of the two uploaded sessions.
    assert body["total_reps"] == s1["total_reps"] + s2["total_reps"]
    assert body["favorite_exercise"] is not None
    assert body["per_exercise"], "expected per-exercise breakdown"

    # Each exercise appears in both sessions -> sessions_count == 2.
    top = body["per_exercise"][0]
    assert top["sessions_count"] == 2
    assert top["total_reps"] > 0
    # per_exercise is sorted by total duration descending.
    durations = [e["total_duration_seconds"] for e in body["per_exercise"]]
    assert durations == sorted(durations, reverse=True)


@pytest.mark.skipif(not _HAS_WEIGHTS, reason="model_weights.pt not present")
async def test_summary_is_user_scoped(client):
    owner = await _auth_headers(client, email="owner2@example.com")
    await _upload(client, owner)

    other = await _auth_headers(client, email="other2@example.com")
    body = (await client.get("/analytics/summary", headers=other)).json()
    assert body["total_sessions"] == 0
    assert body["per_exercise"] == []
