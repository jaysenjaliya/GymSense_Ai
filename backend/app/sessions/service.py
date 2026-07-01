"""Session orchestration: drives the ML pipeline and persists results.

`analyze_csv` is a pure, CPU-bound function (parse + ML pipeline + analytics) meant
to run in a threadpool so it never blocks the event loop. The async functions handle
MongoDB persistence and retrieval, always scoped to the owning user.
"""
import io
from datetime import datetime, timezone

import pandas as pd
from bson import ObjectId
from bson.errors import InvalidId

from app.analytics.calories import estimate_calories
from app.database import get_db
from app.ml.pipeline import run_pipeline
from app.ml.preprocessing import CSVValidationError
from app.sessions.schemas import ExerciseResult, SessionResult, SessionSummary
from app.users.schemas import UserPublic


def _build_summary(n_exercises: int, active_seconds: float, total_reps: int,
                   total_calories: float) -> str:
    minutes = active_seconds / 60.0
    return (
        f"Completed {n_exercises} exercise(s) with {total_reps} total reps in "
        f"{minutes:.1f} active minutes, burning ~{total_calories:.0f} kcal."
    )


def analyze_csv(raw_csv: bytes, weight_kg: float) -> dict:
    """Parse a CSV and run the full pipeline + calorie analytics (CPU-bound, sync).

    Returns a plain dict of analytics ready to persist. Raises `CSVValidationError`
    on unreadable or schema-invalid input.
    """
    try:
        df = pd.read_csv(io.BytesIO(raw_csv))
    except Exception as exc:  # malformed CSV
        raise CSVValidationError(f"Could not parse CSV: {exc}") from exc

    result = run_pipeline(df)

    exercises = [
        {
            "exercise": e.exercise,
            "sets": e.sets,
            "reps": e.reps,
            "duration_seconds": e.duration_seconds,
            "estimated_calories": estimate_calories(e.exercise, e.duration_seconds, weight_kg),
        }
        for e in result.exercises
    ]
    total_calories = round(sum(e["estimated_calories"] for e in exercises), 2)

    return {
        "total_duration_seconds": result.total_duration_seconds,
        "active_duration_seconds": result.active_duration_seconds,
        "total_reps": result.total_reps,
        "total_estimated_calories": total_calories,
        "n_windows": result.n_windows,
        "exercises": exercises,
        "summary": _build_summary(
            len(exercises), result.active_duration_seconds, result.total_reps, total_calories
        ),
    }


async def save_session(user: UserPublic, filename: str | None, analytics: dict) -> SessionResult:
    """Persist a session doc + per-exercise logs, and return the full result."""
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {"user_id": user.id, "filename": filename, "created_at": now, **analytics}

    res = await db.sessions.insert_one(doc)
    session_id = str(res.inserted_id)

    if analytics["exercises"]:
        await db.exercise_logs.insert_many([
            {"session_id": session_id, "user_id": user.id, "created_at": now, **ex}
            for ex in analytics["exercises"]
        ])

    return SessionResult(
        id=session_id,
        created_at=now,
        filename=filename,
        total_duration_seconds=analytics["total_duration_seconds"],
        active_duration_seconds=analytics["active_duration_seconds"],
        total_reps=analytics["total_reps"],
        total_estimated_calories=analytics["total_estimated_calories"],
        exercises=[ExerciseResult(**ex) for ex in analytics["exercises"]],
        summary=analytics["summary"],
    )


async def list_sessions(user_id: str) -> list[SessionSummary]:
    """Return the user's sessions, newest first."""
    cursor = get_db().sessions.find({"user_id": user_id}).sort("created_at", -1)
    summaries: list[SessionSummary] = []
    async for doc in cursor:
        summaries.append(
            SessionSummary(
                id=str(doc["_id"]),
                created_at=doc["created_at"],
                total_duration_seconds=doc["total_duration_seconds"],
                exercise_count=len(doc.get("exercises", [])),
                total_reps=doc["total_reps"],
                total_estimated_calories=doc["total_estimated_calories"],
            )
        )
    return summaries


async def get_session(user_id: str, session_id: str) -> SessionResult | None:
    """Fetch a single session by id, scoped to the owning user."""
    try:
        oid = ObjectId(session_id)
    except (InvalidId, TypeError):
        return None
    doc = await get_db().sessions.find_one({"_id": oid, "user_id": user_id})
    if doc is None:
        return None
    return SessionResult(
        id=str(doc["_id"]),
        created_at=doc["created_at"],
        filename=doc.get("filename"),
        total_duration_seconds=doc["total_duration_seconds"],
        active_duration_seconds=doc["active_duration_seconds"],
        total_reps=doc["total_reps"],
        total_estimated_calories=doc["total_estimated_calories"],
        exercises=[ExerciseResult(**ex) for ex in doc.get("exercises", [])],
        summary=doc["summary"],
    )
