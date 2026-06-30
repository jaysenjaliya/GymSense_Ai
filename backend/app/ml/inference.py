"""PyTorch model loading and offline inference over windowed sensor data.

Treats the pretrained RecGym classifier as a given artifact (.pt). Loads it once
and runs forward passes on prepared windows — does not redesign the architecture.
"""
import torch

from app.config import get_settings

_model = None


def load_model():
    """Load the pretrained .pt model once (lazy singleton)."""
    global _model
    if _model is None:
        path = get_settings().ML_MODEL_PATH
        # TODO: load the model (torch.load / torch.jit.load) and set eval mode.
        # _model = torch.jit.load(path); _model.eval()
        ...
    return _model


@torch.no_grad()
def predict(windows) -> list[int]:
    """Run inference, returning a predicted class index per window."""
    # TODO: tensorize windows, forward pass, argmax over logits
    ...
