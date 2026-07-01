"""Tests for model loading and inference output shape/labels."""
import os

import numpy as np
import pytest

from app.config import get_settings
from app.ml import inference
from app.ml.model import build_model
from app.ml.schema import EXERCISE_LABELS, N_CHANNELS, WINDOW_SIZE

_HAS_WEIGHTS = os.path.isfile(get_settings().ML_MODEL_PATH)


def test_build_model_output_shape():
    import torch

    model = build_model().eval()
    with torch.no_grad():
        out = model(torch.randn(2, 1, WINDOW_SIZE, N_CHANNELS))
    assert out.shape == (2, len(EXERCISE_LABELS))


def test_predict_empty_returns_empty():
    assert inference.predict(np.empty((0, 1, WINDOW_SIZE, N_CHANNELS), dtype="float32")) == []


@pytest.mark.skipif(not _HAS_WEIGHTS, reason="model_weights.pt not present")
def test_predict_with_real_weights_returns_valid_labels():
    rng = np.random.default_rng(0)
    windows = rng.normal(size=(4, 1, WINDOW_SIZE, N_CHANNELS)).astype("float32")
    preds = inference.predict(windows)
    assert len(preds) == 4
    assert all(0 <= p < len(EXERCISE_LABELS) for p in preds)
