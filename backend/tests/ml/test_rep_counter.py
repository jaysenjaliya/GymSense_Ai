"""Tests for peak-detection rep counting (synthetic signals -> known counts)."""
import numpy as np

from app.ml.rep_counter import accel_magnitude, count_reps
from app.ml.schema import EXPECTED_COLUMNS, N_CHANNELS, SAMPLING_RATE_HZ


def _periodic_signal(n_cycles: int, samples_per_cycle: int) -> np.ndarray:
    """Build a (T, 7) signal whose accel-magnitude has exactly `n_cycles` peaks."""
    t = np.arange(n_cycles * samples_per_cycle)
    # Offset keeps magnitude strictly positive so |·| doesn't double the peaks.
    a_x = 2.0 + np.sin(2 * np.pi * t / samples_per_cycle)
    sig = np.zeros((t.size, N_CHANNELS), dtype=np.float32)
    sig[:, EXPECTED_COLUMNS.index("A_x")] = a_x
    return sig


def test_accel_magnitude_matches_euclidean_norm():
    sig = np.zeros((3, N_CHANNELS), dtype=np.float32)
    sig[:, EXPECTED_COLUMNS.index("A_x")] = 3.0
    sig[:, EXPECTED_COLUMNS.index("A_y")] = 4.0
    assert np.allclose(accel_magnitude(sig), 5.0)


def test_count_reps_matches_number_of_cycles():
    # 10 clean cycles, 1s each (20 samples) -> expect 10 reps.
    sig = _periodic_signal(n_cycles=10, samples_per_cycle=SAMPLING_RATE_HZ)
    assert count_reps(sig) == 10


def test_count_reps_empty_signal():
    assert count_reps(np.empty((0, N_CHANNELS), dtype=np.float32)) == 0
