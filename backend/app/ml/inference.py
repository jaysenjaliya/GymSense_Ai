"""PyTorch model loading and offline inference over windowed sensor data.

Loads the pretrained RecGym `PostFusion` weights (a `state_dict`) once and runs
forward passes on prepared windows. CPU-only by default; the model is tiny (~1.1M
params) so this is fast enough for request-time inference.
"""
import numpy as np
import torch

from app.config import get_settings
from app.ml.model import build_model
from app.ml.schema import EXERCISE_LABELS, N_CHANNELS

_model: torch.nn.Module | None = None
_device = torch.device("cpu")


def load_model() -> torch.nn.Module:
    """Load the pretrained model once (lazy singleton) and set eval mode."""
    global _model
    if _model is None:
        model = build_model(n_classes=len(EXERCISE_LABELS), in_chans=N_CHANNELS)
        state = torch.load(
            get_settings().ML_MODEL_PATH, map_location=_device, weights_only=True
        )
        model.load_state_dict(state)
        model.eval()
        _model = model.to(_device)
    return _model


@torch.no_grad()
def predict(windows: np.ndarray) -> list[int]:
    """Run inference over windows of shape (N, 1, 80, 7); return class index per window."""
    if windows.size == 0:
        return []
    model = load_model()
    tensor = torch.as_tensor(windows, dtype=torch.float32, device=_device)
    logits = model(tensor)
    return logits.argmax(dim=1).cpu().tolist()
