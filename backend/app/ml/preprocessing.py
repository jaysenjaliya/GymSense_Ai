"""CSV validation, cleaning, and sliding-window generation for model input."""
import pandas as pd


def validate_csv(df: pd.DataFrame) -> None:
    """Raise if required columns (app.ml.schema.EXPECTED_COLUMNS) are missing."""
    # TODO
    ...


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean/normalize/filter raw sensor data into model-ready features."""
    # TODO
    ...


def make_windows(df: pd.DataFrame):
    """Generate fixed-size sliding windows (WINDOW_SIZE / WINDOW_STRIDE)."""
    # TODO: return an array-like of shape (n_windows, window_size, n_features)
    ...
