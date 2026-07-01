"""MET-based calorie estimation.

Calories = MET × body_weight_kg × duration_hours (the standard compendium formula).
MET values are approximate resistance/cardio equivalents keyed by the RecGym labels;
they are good enough for relative progress tracking, not clinical accuracy.
"""

# Metabolic Equivalent of Task per exercise label (approximate).
MET_BY_EXERCISE: dict[str, float] = {
    "Adductor": 4.0,
    "ArmCurl": 3.5,
    "BenchPress": 5.0,
    "LegCurl": 4.0,
    "LegPress": 5.0,
    "Null": 1.0,          # rest / non-exercise
    "Riding": 7.0,        # stationary cycling, moderate
    "RopeSkipping": 11.0,
    "Running": 9.8,
    "Squat": 5.0,
    "StairClimber": 9.0,
    "Walking": 3.5,
}

DEFAULT_MET = 3.5


def estimate_calories(exercise: str, duration_seconds: float, weight_kg: float) -> float:
    """Estimate kcal burned for one exercise given its duration and the user's weight."""
    met = MET_BY_EXERCISE.get(exercise, DEFAULT_MET)
    hours = duration_seconds / 3600.0
    return round(met * weight_kg * hours, 2)
