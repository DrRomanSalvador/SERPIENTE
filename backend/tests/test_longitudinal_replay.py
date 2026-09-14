from datetime import datetime, timedelta, timezone

from app.contracts import Observation
from app.longitudinal import PointInTimeStore, LongitudinalStateBuilder


def make(i: int, value: float):
    t = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=i)
    return Observation("s", "d", "v", "semantic", "unit", "Ceuta", t, t, t + timedelta(hours=1), "v1", 0, value, ("official:s",))


def test_history_and_latest_snapshot_are_distinct():
    store = PointInTimeStore(); rows = [make(i, float(i)) for i in range(10)]; store.add(rows)
    as_of = rows[-1].event_time + timedelta(hours=2)
    assert len(store.history_at(as_of)) == 10
    assert len(store.at(as_of)) == 1
    state = LongitudinalStateBuilder().build(store.history_at(as_of), as_of=as_of)
    assert state.trends["v"] > 0
    assert state.lags["v"]
