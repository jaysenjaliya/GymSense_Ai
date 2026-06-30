"""ML pipeline data contracts: expected CSV columns, feature schema, label set.

Defining these here keeps the pipeline self-describing and FastAPI-independent.
"""

# 12 gym exercises classified by the pretrained RecGym model.
# TODO: replace with the exact label ordering used during training.
EXERCISE_LABELS: list[str] = []

# Expected input feature/column names for the wearable CSV.
# TODO: fill in the known input feature schema (e.g. accel/gyro axes, timestamp).
EXPECTED_COLUMNS: list[str] = []

# Sliding-window configuration used to feed the model.
# TODO: confirm window size / stride / sampling rate from the model's training setup.
WINDOW_SIZE: int = 0
WINDOW_STRIDE: int = 0
SAMPLING_RATE_HZ: int = 0
