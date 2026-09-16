from datetime import datetime, timezone

import pytest

from app.contracts import Event, Signal
from app.engines import PatternEngine, PropagationLink, SignalEngine, TrajectoryEngine


def _signal(signal_id: str, domain: str, anomaly: float = 0.8) -> Signal:
    return Signal(
        signal_id=signal_id,
        event_id=f"event-{signal_id}",
        domain=domain,
        variable_id=f"var-{signal_id}",
        value=anomaly,
        z_score=2.0,
        anomaly_score=anomaly,
        trend=1.0,
        acceleration=0.1,
        volatility=1.0,
        provenance=(f"source-{signal_id}",),
    )


def test_cross_domain_propagation_requires_explicit_evidence() -> None:
    signals = [_signal("s1", "health"), _signal("s2", "environment")]
    pattern = PatternEngine().detect(signals)
    trajectory = TrajectoryEngine().build(pattern, signals, regime="BASELINE")
    assert trajectory.propagation == 0.0
    assert trajectory.cascade_score == 0.0


def test_explicit_propagation_link_creates_descriptive_network_signal() -> None:
    signals = [_signal("s1", "health"), _signal("s2", "environment")]
    pattern = PatternEngine().detect(signals)
    link = PropagationLink("s1", "s2", lag="P1D", evidence_id="evidence-1")
    trajectory = TrajectoryEngine().build(
        pattern,
        signals,
        regime="BASELINE",
        propagation_links=(link,),
    )
    assert trajectory.propagation == 1.0
    assert trajectory.cascade_score > 0.0
    assert "evidence-1" in trajectory.provenance


def test_propagation_link_cannot_reference_unknown_signal() -> None:
    signals = [_signal("s1", "health"), _signal("s2", "environment")]
    pattern = PatternEngine().detect(signals)
    link = PropagationLink("s1", "unknown", lag="P1D", evidence_id="evidence-1")
    with pytest.raises(ValueError, match="absent signal"):
        TrajectoryEngine().build(pattern, signals, regime="BASELINE", propagation_links=(link,))
