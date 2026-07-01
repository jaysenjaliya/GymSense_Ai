"""Tests for registration, login, refresh, and the protected /auth/me route."""
from tests.conftest import valid_user_payload


async def _register(client, **overrides):
    return await client.post("/auth/register", json=valid_user_payload(**overrides))


async def test_register_returns_public_profile_without_password(client):
    resp = await _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "jay@example.com"
    assert body["height_cm"] == 180.0
    assert body["fitness_goal"] == "hypertrophy"
    assert "id" in body and body["id"]
    # The hash must never leak.
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate_email_conflicts(client):
    assert (await _register(client)).status_code == 201
    dup = await _register(client)
    assert dup.status_code == 409


async def test_register_rejects_invalid_fitness_goal(client):
    resp = await _register(client, fitness_goal="bulking")
    assert resp.status_code == 422


async def test_register_rejects_nonpositive_measurements(client):
    assert (await _register(client, height_cm=0)).status_code == 422
    assert (await _register(client, weight_kg=-5)).status_code == 422


async def test_login_returns_token_pair(client):
    await _register(client)
    resp = await client.post(
        "/auth/login",
        json={"email": "jay@example.com", "password": "supersecret123"},
    )
    assert resp.status_code == 200
    token = resp.json()
    assert token["token_type"] == "bearer"
    assert token["access_token"] and token["refresh_token"]


async def test_login_wrong_password_unauthorized(client):
    await _register(client)
    resp = await client.post(
        "/auth/login",
        json={"email": "jay@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_me_requires_token(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_returns_profile_with_valid_token(client):
    await _register(client)
    login = await client.post(
        "/auth/login",
        json={"email": "jay@example.com", "password": "supersecret123"},
    )
    access = login.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "jay@example.com"


async def test_refresh_issues_working_access_token(client):
    await _register(client)
    login = await client.post(
        "/auth/login",
        json={"email": "jay@example.com", "password": "supersecret123"},
    )
    refresh_token = login.json()["refresh_token"]

    refreshed = await client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refreshed.status_code == 200
    new_access = refreshed.json()["access_token"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me.status_code == 200


async def test_refresh_rejects_access_token_as_refresh(client):
    await _register(client)
    login = await client.post(
        "/auth/login",
        json={"email": "jay@example.com", "password": "supersecret123"},
    )
    access = login.json()["access_token"]
    # An access token must not be accepted at the refresh endpoint.
    resp = await client.post("/auth/refresh", json={"refresh_token": access})
    assert resp.status_code == 401
