"""CSV validation, cleaning, and sliding-window generation for model input.

Mirrors the training pipeline exactly: select the 7 sensor columns in order, drop
partial trailing windows, reshape to (N, 1, WINDOW_SIZE, N_CHANNELS). NO scaling.
"""
import numpy as np
import pandas as pd

from app.ml.schema import EXPECTED_COLUMNS, N_CHANNELS, WINDOW_SIZE


class CSVValidationError(ValueError):
    """Raised when an uploaded CSV does not match the expected sensor schema."""


def validate_csv(df: pd.DataFrame) -> None:
    """Ensure all required sensor columns are present and there is enough data."""
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise CSVValidationError(
            f"CSV is missing required columns: {missing}. "
            f"Expected columns: {EXPECTED_COLUMNS}"
        )
    usable = df.dropna(subset=EXPECTED_COLUMNS)
    if len(usable) < WINDOW_SIZE:
        raise CSVValidationError(
            f"CSV has only {len(usable)} valid rows; at least {WINDOW_SIZE} "
            "are required to form one window."
        )


def preprocess(df: pd.DataFrame) -> np.ndarray:
    """Select sensor columns (in order), drop NaN rows, return raw float32 array.

    Returns an array of shape (T, N_CHANNELS). No normalization is applied — the
    model was trained on raw sensor values.
    """
    clean = df.dropna(subset=EXPECTED_COLUMNS)
    return clean[EXPECTED_COLUMNS].to_numpy(dtype=np.float32)


def make_windows(signal: np.ndarray) -> np.ndarray:
    """Split (T, C) raw signal into non-overlapping windows.

    Trailing rows that don't fill a full window are dropped (matching training).
    Returns shape (n_windows, 1, WINDOW_SIZE, N_CHANNELS) ready for the model.
    """
    if signal.ndim != 2 or signal.shape[1] != N_CHANNELS:
        raise CSVValidationError(
            f"Expected signal shape (T, {N_CHANNELS}), got {signal.shape}"
        )
    n_full = (signal.shape[0] // WINDOW_SIZE) * WINDOW_SIZE
    trimmed = signal[:n_full]
    windows = trimmed.reshape(-1, WINDOW_SIZE, N_CHANNELS)
    return windows.reshape(-1, 1, WINDOW_SIZE, N_CHANNELS)
