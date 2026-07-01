"""Tests for the CSV upload -> pipeline -> persisted results flow.

Runs the real ML model against the compact sample fixture through the HTTP layer
(in-memory Mongo via mongomock-motor from conftest).
"""
import os

import pytest

from app.config import get_settings
from tests.conftest import valid_user_payload

FIXTURE = os.path.join(os.path.dirname(__file__), "data", "sample_session.csv")
_HAS_WEIGHTS = os.path.isfile(get_settings().ML_MODEL_PATH)
pytestmark = pytest.mark.skipif(not _HAS_WEIGHTS, reason="model_weights.pt not present")


async def _auth_headers(client, email="lifter@example.com"):
    await client.post("/auth/register", json=valid_user_payload(email=email))
    login = await client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _upload_fixture(client, headers):
    with open(FIXTURE, "rb") as f:
        data = f.read()
    return await client.post(
        "/sessions/upload",
        headers=headers,
        files={"file": ("sample_session.csv", data, "text/csv")},
    )


async def test_upload_returns_session_result(client):
    headers = await _auth_headers(client)
    resp = await _upload_fixture(client, headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["exercises"], "expected at least one detected exercise"
    assert body["total_reps"] >= 0
    assert body["total_duration_seconds"] > 0
    assert body["total_estimated_calories"] >= 0
    # Every exercise carries the full breakdown.
    for ex in body["exercises"]:
        assert {"exercise", "sets", "reps", "duration_seconds", "estimated_calories"} <= ex.keys()
        assert ex["exercise"] != "Null"


async def test_upload_requires_auth(client):
    resp = await _upload_fixture(client, headers={})
    assert resp.status_code == 401


async def test_upload_rejects_non_csv(client):
    headers = await _auth_headers(client)
    resp = await client.post(
        "/sessions/upload",
        headers=headers,
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400


async def test_upload_rejects_bad_schema(client):
    headers = await _auth_headers(client)
    resp = await client.post(
        "/sessions/upload",
        headers=headers,
        files={"file": ("bad.csv", b"foo,bar\n1,2\n3,4\n", "text/csv")},
    )
    assert resp.status_code == 422


async def test_list_and_get_session(client):
    headers = await _auth_headers(client)
    created = (await _upload_fixture(client, headers)).json()

    listing = await client.get("/sessions", headers=headers)
    assert listing.status_code == 200
    items = listing.json()
    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["exercise_count"] == len(created["exercises"])

    fetched = await client.get(f"/sessions/{created['id']}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


async def test_sessions_are_user_scoped(client):
    owner = await _auth_headers(client, email="owner@example.com")
    created = (await _upload_fixture(client, owner)).json()

    other = await _auth_headers(client, email="intruder@example.com")
    # Other user can't read it, and their own listing is empty.
    assert (await client.get(f"/sessions/{created['id']}", headers=other)).status_code == 404
    assert (await client.get("/sessions", headers=other)).json() == []
