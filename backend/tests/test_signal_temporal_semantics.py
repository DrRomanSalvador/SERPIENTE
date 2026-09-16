from datetime import datetime, timezone

from app.contracts import Event
from app.engines import SignalEngine


def test_signal_inherits_event_time_for_temporal_semantics():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    event = Event("event-1", now, "Ceuta", "health", "demand", 10.0, ("obs-1",), ("source:v1",))
    signal = SignalEngine().from_state(event, variable_id="hospital_demand", value=10.0, baseline=9.0, trend=1.0, acceleration=0.2, volatility=1.0, provenance=("source:v1",))
    assert signal.event_time == now
