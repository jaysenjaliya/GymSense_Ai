"""ML pipeline data contracts: expected CSV columns, feature schema, label set.

All values are taken directly from the RecGym training notebook
(Hybrid_CNN_PyTorch). Keep this module free of heavy imports so it stays a cheap,
self-describing source of truth for the pipeline.
"""

# Input feature columns, in the exact order the model expects (sensor="combine").
# 6 IMU channels (accelerometer + gyroscope) + 1 capacitive channel.
EXPECTED_COLUMNS: list[str] = ["A_x", "A_y", "A_z", "G_x", "G_y", "G_z", "C_1"]
N_CHANNELS: int = len(EXPECTED_COLUMNS)  # 7

# The 12 classes, ordered to match the model's output indices (0..11).
# Derived from the training pipeline: alphabetical sort of workout names, 0-based.
EXERCISE_LABELS: list[str] = [
    "Adductor",      # 0
    "ArmCurl",       # 1
    "BenchPress",    # 2
    "LegCurl",       # 3
    "LegPress",      # 4
    "Null",          # 5  (rest / non-exercise)
    "Riding",        # 6
    "RopeSkipping",  # 7
    "Running",       # 8
    "Squat",         # 9
    "StairClimber",  # 10
    "Walking",       # 11
]

LABEL_TO_INDEX: dict[str, int] = {name: i for i, name in enumerate(EXERCISE_LABELS)}

# The "Null" class marks rest / no meaningful activity — excluded from exercise
# segmentation, rep counting, and analytics.
NULL_LABEL: str = "Null"
NULL_INDEX: int = LABEL_TO_INDEX[NULL_LABEL]

# Sliding-window config used both at training time and for inference.
# 80 samples per window, stride 80 (no overlap), raw values (NO scaling).
WINDOW_SIZE: int = 80
WINDOW_STRIDE: int = 80

# Sampling rate of the wearable. NOTE: not stated in the training notebook; only
# affects duration/calorie math (NOT classification). Confirm against the RecGym
# dataset and override via config if needed.
SAMPLING_RATE_HZ: int = 20

# Accelerometer / gyroscope channel groupings (used for rep-counting signals).
ACCEL_COLUMNS: list[str] = ["A_x", "A_y", "A_z"]
GYRO_COLUMNS: list[str] = ["G_x", "G_y", "G_z"]
