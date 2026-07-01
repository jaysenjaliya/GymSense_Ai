"""Exercise segmentation — group the smoothed prediction sequence into contiguous
exercise segments.

Each window represents WINDOW_SIZE consecutive samples, so a segment spanning
window indices [start, end] covers samples [start*WINDOW_SIZE, (end+1)*WINDOW_SIZE).
"""
from dataclasses import dataclass

from app.ml.schema import EXERCISE_LABELS, NULL_INDEX, WINDOW_SIZE


@dataclass
class Segment:
    label_index: int
    label: str
    start_window: int  # inclusive
    end_window: int    # inclusive
    n_windows: int

    @property
    def start_sample(self) -> int:
        return self.start_window * WINDOW_SIZE

    @property
    def end_sample(self) -> int:
        """Exclusive end sample index."""
        return (self.end_window + 1) * WINDOW_SIZE


def segment(predictions: list[int], *, include_null: bool = False) -> list[Segment]:
    """Collapse consecutive equal predictions into labelled segments.

    By default the `Null` (rest) class is excluded from the returned segments.
    """
    segments: list[Segment] = []
    if not predictions:
        return segments

    run_start = 0
    for i in range(1, len(predictions) + 1):
        if i == len(predictions) or predictions[i] != predictions[run_start]:
            label_idx = predictions[run_start]
            if include_null or label_idx != NULL_INDEX:
                segments.append(
                    Segment(
                        label_index=label_idx,
                        label=EXERCISE_LABELS[label_idx],
                        start_window=run_start,
                        end_window=i - 1,
                        n_windows=i - run_start,
                    )
                )
            run_start = i
    return segments
