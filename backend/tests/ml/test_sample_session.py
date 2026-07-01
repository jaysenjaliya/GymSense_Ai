"""Integration test: run the full ML pipeline on the real sample session fixture."""
import os

import pandas as pd
import pytest

from app.config import get_settings
from app.ml import inference, preprocessing, segmentation, smoothing
from app.ml.schema import EXERCISE_LABELS

FIXTURE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_session.csv")
_HAS_WEIGHTS = os.path.isfile(get_settings().ML_MODEL_PATH)


@pytest.mark.skipif(not _HAS_WEIGHTS, reason="model_weights.pt not present")
def test_pipeline_on_real_sample_session():
    df = pd.read_csv(FIXTURE)
    preprocessing.validate_csv(df)

    windows = preprocessing.make_windows(preprocessing.preprocess(df))
    assert windows.shape[1:] == (1, 80, 7)

    preds = inference.predict(windows)
    assert len(preds) == windows.shape[0]
    assert all(0 <= p < len(EXERCISE_LABELS) for p in preds)

    segments = segmentation.segment(smoothing.smooth_predictions(preds))
    # The fixture contains real exercises, so at least one non-Null segment is found.
    assert segments, "expected at least one exercise segment"
    assert all(s.label != "Null" for s in segments)
