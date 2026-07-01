"""Tests for smoothing and segmenting predictions into contiguous exercise runs."""
from app.ml.schema import EXERCISE_LABELS, NULL_INDEX, WINDOW_SIZE
from app.ml.segmentation import segment
from app.ml.smoothing import smooth_predictions


def test_smoothing_removes_single_outlier():
    preds = [8, 8, 3, 8, 8]  # the lone `3` should be voted out
    assert smooth_predictions(preds, window=3) == [8, 8, 8, 8, 8]


def test_segment_groups_contiguous_runs_and_maps_samples():
    # two Squat windows (label 9) then three Running windows (label 8)
    segs = segment([9, 9, 8, 8, 8])
    assert [(s.label, s.n_windows) for s in segs] == [
        (EXERCISE_LABELS[9], 2),
        (EXERCISE_LABELS[8], 3),
    ]
    first = segs[0]
    assert first.start_sample == 0
    assert first.end_sample == 2 * WINDOW_SIZE


def test_segment_excludes_null_by_default():
    segs = segment([NULL_INDEX, NULL_INDEX, 9, NULL_INDEX])
    assert len(segs) == 1
    assert segs[0].label == EXERCISE_LABELS[9]

    with_null = segment([NULL_INDEX, 9], include_null=True)
    assert len(with_null) == 2
