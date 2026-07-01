"""End-to-end ML orchestration for a completed session.

Chains the Phase-2 steps into a single call that turns a raw sensor DataFrame into
per-exercise aggregates. Kept free of FastAPI/DB concerns so it can be reused for
future real-time streaming.

Order: validate -> preprocess -> window -> infer -> smooth -> segment -> rep count.
"""
from dataclasses import dataclass

import pandas as pd

from app.ml import inference, preprocessing, segmentation, smoothing
from app.ml.rep_counter import count_reps
from app.ml.schema import SAMPLING_RATE_HZ, WINDOW_SIZE


def windows_to_seconds(n_windows: int) -> float:
    return round(n_windows * WINDOW_SIZE / SAMPLING_RATE_HZ, 2)


@dataclass
class ExerciseAggregate:
    exercise: str
    sets: int              # number of contiguous segments of this exercise
    reps: int              # total reps across those segments
    duration_seconds: float


@dataclass
class PipelineResult:
    total_duration_seconds: float   # whole session (incl. rest)
    active_duration_seconds: float  # exercise time only
    total_reps: int
    n_windows: int
    exercises: list[ExerciseAggregate]


def run_pipeline(df: pd.DataFrame, *, smoothing_window: int = 5) -> PipelineResult:
    """Run the full pipeline on a raw sensor DataFrame."""
    preprocessing.validate_csv(df)
    signal = preprocessing.preprocess(df)
    windows = preprocessing.make_windows(signal)

    predictions = inference.predict(windows)
    smoothed = smoothing.smooth_predictions(predictions, window=smoothing_window)
    segments = segmentation.segment(smoothed)  # Null excluded

    agg: dict[str, dict] = {}
    for seg in segments:
        reps = count_reps(signal[seg.start_sample:seg.end_sample])
        bucket = agg.setdefault(seg.label, {"sets": 0, "reps": 0, "dur": 0.0})
        bucket["sets"] += 1
        bucket["reps"] += reps
        bucket["dur"] += windows_to_seconds(seg.n_windows)

    exercises = [
        ExerciseAggregate(
            exercise=label,
            sets=v["sets"],
            reps=v["reps"],
            duration_seconds=round(v["dur"], 2),
        )
        for label, v in agg.items()
    ]
    exercises.sort(key=lambda e: e.duration_seconds, reverse=True)

    active = round(sum(e.duration_seconds for e in exercises), 2)
    total = windows_to_seconds(len(smoothed))
    total_reps = sum(e.reps for e in exercises)

    return PipelineResult(
        total_duration_seconds=total,
        active_duration_seconds=active,
        total_reps=total_reps,
        n_windows=len(smoothed),
        exercises=exercises,
    )
