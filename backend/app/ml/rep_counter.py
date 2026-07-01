"""Rep counting via signal peak detection (SciPy find_peaks).

Independent of the ML model: operates on the accelerometer-magnitude signal within
a single exercise segment. The classifier tells us *what* exercise; peak detection
on the periodic sensor signal tells us *how many reps*.
"""
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks

from app.ml.schema import ACCEL_COLUMNS, EXPECTED_COLUMNS, SAMPLING_RATE_HZ


def accel_magnitude(signal: np.ndarray) -> np.ndarray:
    """Compute accelerometer magnitude sqrt(A_x^2 + A_y^2 + A_z^2) from (T, C) signal."""
    idx = [EXPECTED_COLUMNS.index(c) for c in ACCEL_COLUMNS]
    accel = signal[:, idx]
    return np.sqrt((accel ** 2).sum(axis=1))


def _smooth(x: np.ndarray, size: int) -> np.ndarray:
    if size <= 1 or x.size == 0:
        return x
    return uniform_filter1d(x, size=size, mode="nearest")


def count_reps(
    signal: np.ndarray,
    *,
    smooth_size: int = 5,
    min_distance_s: float = 0.4,
    prominence: float | None = None,
) -> int:
    """Count reps as peaks in the smoothed accelerometer-magnitude signal.

    `signal` is the raw (T, C) sensor array for one exercise segment.
    `min_distance_s` enforces a minimum time between reps (default 0.4s ≈ 150 rpm cap).
    `prominence` defaults to half the signal's standard deviation when not given.
    """
    if signal.shape[0] == 0:
        return 0
    mag = _smooth(accel_magnitude(signal), smooth_size)
    if prominence is None:
        prominence = max(float(np.std(mag)) * 0.5, 1e-6)
    distance = max(1, int(round(min_distance_s * SAMPLING_RATE_HZ)))
    peaks, _ = find_peaks(mag, distance=distance, prominence=prominence)
    return int(len(peaks))
