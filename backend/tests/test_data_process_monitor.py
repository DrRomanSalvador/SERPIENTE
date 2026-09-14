from datetime import datetime, timedelta, timezone

from app.contracts import Observation
from app.quality import DataProcessMonitor


def make(i: int, *, version="v1", missing=False):
    t = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=i)
    return Observation("s", "d", "v", "semantic", "unit", "Ceuta", t, t, t, version, 0, None if missing else 1.0, ("official",), missing=missing)


def test_cadence_or_missingness_change_is_flagged():
    history = [make(i) for i in range(6)] + [make(20, missing=True), make(21, missing=True)]
    assessment = DataProcessMonitor().assess(history)
    assert assessment.process_change
    assert assessment.severity > 0


def test_stable_source_is_not_flagged():
    history = [make(i) for i in range(10)]
    assert not DataProcessMonitor().assess(history).process_change
