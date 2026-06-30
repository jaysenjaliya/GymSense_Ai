"""Prediction smoothing — reduce per-window jitter before segmentation.

Applies a majority vote / rolling mode over the sequence of window predictions.
"""


def smooth_predictions(predictions: list[int], window: int = 5) -> list[int]:
    """Return a smoothed prediction sequence (rolling majority vote)."""
    # TODO
    ...
