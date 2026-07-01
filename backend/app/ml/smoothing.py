"""Prediction smoothing — reduce per-window jitter before segmentation.

Applies a centered rolling majority vote over the sequence of window predictions.
"""
from collections import Counter


def smooth_predictions(predictions: list[int], window: int = 5) -> list[int]:
    """Return a smoothed prediction sequence via centered rolling majority vote.

    `window` is the number of neighbouring predictions considered (clamped to the
    sequence length). A window <= 1 returns the input unchanged.
    """
    n = len(predictions)
    if window <= 1 or n == 0:
        return list(predictions)

    half = window // 2
    smoothed: list[int] = []
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        counts = Counter(predictions[lo:hi])
        # Ties broken by the smaller class index for determinism.
        best = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        smoothed.append(best)
    return smoothed
