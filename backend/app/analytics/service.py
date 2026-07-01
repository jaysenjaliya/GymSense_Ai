"""Analytics computation: cross-session aggregate metrics.

Per-session analytics (duration, sets/reps, calories) are produced by the ML
pipeline + `app.analytics.calories` during upload. This module aggregates the
persisted `sessions` and `exercise_logs` into a dashboard-level summary.

Aggregation is done in Python (histories are small per user) so it works
identically against real MongoDB and the in-memory test double.
"""
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.analytics.schemas import ExerciseAggregate, UserAnalyticsSummary


def _aware(dt: datetime) -> datetime:
    """Treat naive datetimes (as returned by MongoDB) as UTC."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def build_user_summary(user_id: str) -> UserAnalyticsSummary:
    """Aggregate all of a user's sessions + exercise logs into a summary."""
    db = get_db()

    sessions = [s async for s in db.sessions.find({"user_id": user_id})]
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    created_ats = [_aware(s["created_at"]) for s in sessions]
    sessions_last_7_days = sum(1 for c in created_ats if c >= week_ago)

    # Per-exercise aggregation from exercise_logs.
    buckets: dict[str, dict] = {}
    async for log in db.exercise_logs.find({"user_id": user_id}):
        b = buckets.setdefault(
            log["exercise"],
            {"sessions": set(), "sets": 0, "reps": 0, "dur": 0.0, "cal": 0.0},
        )
        b["sessions"].add(log["session_id"])
        b["sets"] += log["sets"]
        b["reps"] += log["reps"]
        b["dur"] += log["duration_seconds"]
        b["cal"] += log["estimated_calories"]

    per_exercise = [
        ExerciseAggregate(
            exercise=name,
            sessions_count=len(b["sessions"]),
            total_sets=b["sets"],
            total_reps=b["reps"],
            total_duration_seconds=round(b["dur"], 2),
            total_estimated_calories=round(b["cal"], 2),
        )
        for name, b in buckets.items()
    ]
    per_exercise.sort(key=lambda e: e.total_duration_seconds, reverse=True)

    return UserAnalyticsSummary(
        total_sessions=len(sessions),
        total_active_seconds=round(sum(s["active_duration_seconds"] for s in sessions), 2),
        total_reps=sum(s["total_reps"] for s in sessions),
        total_estimated_calories=round(sum(s["total_estimated_calories"] for s in sessions), 2),
        first_session_at=min(created_ats) if created_ats else None,
        last_session_at=max(created_ats) if created_ats else None,
        sessions_last_7_days=sessions_last_7_days,
        favorite_exercise=per_exercise[0].exercise if per_exercise else None,
        per_exercise=per_exercise,
    )
