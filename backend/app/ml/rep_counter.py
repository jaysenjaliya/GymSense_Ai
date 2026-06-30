"""Rep counting via signal peak detection (SciPy find_peaks).

Independent of the ML model: operates on the smoothed/filtered sensor signal
within a single exercise segment.
"""
from scipy.signal import find_peaks


def count_reps(signal, *, prominence: float | None = None, distance: int | None = None) -> int:
    """Count reps as peaks in the (smoothed) signal for one exercise segment."""
    # TODO: smooth/filter signal, tune find_peaks params per exercise, return count
    peaks, _ = find_peaks(signal, prominence=prominence, distance=distance)
    return len(peaks)
