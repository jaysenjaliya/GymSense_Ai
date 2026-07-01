"""Tests for CSV validation, preprocessing, and sliding-window generation."""
import numpy as np
import pandas as pd
import pytest

from app.ml import preprocessing
from app.ml.preprocessing import CSVValidationError
from app.ml.schema import EXPECTED_COLUMNS, N_CHANNELS, WINDOW_SIZE


def _frame(n_rows: int) -> pd.DataFrame:
    data = {c: np.random.default_rng(0).normal(size=n_rows) for c in EXPECTED_COLUMNS}
    return pd.DataFrame(data)


def test_validate_csv_missing_columns():
    df = _frame(WINDOW_SIZE).drop(columns=["C_1"])
    with pytest.raises(CSVValidationError):
        preprocessing.validate_csv(df)


def test_validate_csv_too_few_rows():
    with pytest.raises(CSVValidationError):
        preprocessing.validate_csv(_frame(WINDOW_SIZE - 1))


def test_make_windows_shape_and_trailing_drop():
    # 250 rows -> 3 full windows of 80 (240 rows), 10 trailing rows dropped.
    sig = preprocessing.preprocess(_frame(250))
    windows = preprocessing.make_windows(sig)
    assert windows.shape == (3, 1, WINDOW_SIZE, N_CHANNELS)


def test_preprocess_preserves_column_order_and_drops_nan():
    df = _frame(WINDOW_SIZE)
    df.loc[0, "A_x"] = np.nan
    arr = preprocessing.preprocess(df)
    assert arr.shape == (WINDOW_SIZE - 1, N_CHANNELS)
    assert arr.dtype == np.float32
