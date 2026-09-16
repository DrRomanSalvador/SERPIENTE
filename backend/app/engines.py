from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from uuid import uuid4

import networkx as nx

from .contracts import Alert, Event, Signal


@dataclass(frozen=True, slots=True)
class Pattern:
    pattern_id: str
    signal_ids: tuple[str, ...]
    domains: tuple[str, ...]
    coherence: float
    disagreement: float
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PropagationLink:
    """Observed or explicitly modelled relation between two signals.

    A link is not a causal claim. It is evidence that a propagation relation is
    present in the supplied graph; causal interpretation remains outside this
    object and requires an explicit causal design.
    """

    source_signal_id: str
    target_signal_id: str
    lag: str
    evidence_id: str

    def __post_init__(self) -> None:
        if not self.source_signal_id or not self.target_signal_id:
            raise ValueError("propagation links require source and target signal IDs")
        if self.source_signal_id == self.target_signal_id:
            raise ValueError("propagation links cannot be self-links")
        if not self.lag or not self.evidence_id:
            raise ValueError("propagation links require lag and evidence ID")


@dataclass(frozen=True, slots=True)
class Trajectory:
    trajectory_id: str
    pattern_id: str
    direction: str
    persistence: float
    acceleration: float
    propagation: float
    cascade_score: float
    regime: str
    provenance: tuple[str, ...]


class EventEngine:
    def normalize(self, observation_ids: tuple[str, ...], *, event_time, geography: str, domain: str, event_type: str, magnitude: float, provenance: tuple[str, ...]) -> Event:
        if not observation_ids or not provenance or not domain:
            raise ValueError("events require observations, domain and provenance")
        return Event(str(uuid4()), event_time, geography, domain, event_type, magnitude, observation_ids, provenance)


class SignalEngine:
    def from_state(self, event: Event, *, variable_id: str, value: float, baseline: float, trend: float, acceleration: float, volatility: float, provenance: tuple[str, ...]) -> Signal:
        for item in (value, baseline, trend, acceleration, volatility):
            if not isfinite(item):
                raise ValueError("signal inputs must be finite")
        z = (value - baseline) / max(volatility, 1e-12)
        anomaly = min(1.0, abs(z) / 4.0)
        return Signal(str(uuid4()), event.event_id, event.domain, variable_id, value, z, anomaly, trend, acceleration, volatility, tuple(dict.fromkeys(provenance + event.provenance)))


class PatternEngine:
    def detect(self, signals: list[Signal]) -> Pattern:
        if not signals:
            raise ValueError("pattern detection requires signals")
        magnitudes = [s.anomaly_score for s in signals]
        spread = (max(magnitudes) - min(magnitudes)) if len(magnitudes) > 1 else 0.0
        coherence = max(0.0, 1.0 - spread)
        provenance = tuple(dict.fromkeys(p for s in signals for p in s.provenance))
        return Pattern(str(uuid4()), tuple(str(s.signal_id) for s in signals), tuple(sorted(set(s.domain for s in signals))), coherence, spread, provenance)


class TrajectoryEngine:
    def build(
        self,
        pattern: Pattern,
        signals: list[Signal],
        *,
        regime: str,
        propagation_links: tuple[PropagationLink, ...] = (),
    ) -> Trajectory:
        if not signals:
            raise ValueError("trajectory detection requires signals")
        signal_ids = {str(signal.signal_id) for signal in signals}
        if not set(pattern.signal_ids).issubset(signal_ids):
            raise ValueError("pattern references signals absent from trajectory input")
        for link in propagation_links:
            if link.source_signal_id not in signal_ids or link.target_signal_id not in signal_ids:
                raise ValueError("propagation link references an absent signal")

        trend = sum(s.trend for s in signals) / len(signals)
        acceleration = sum(s.acceleration for s in signals) / len(signals)
        persistence = min(1.0, sum(1 for s in signals if s.anomaly_score >= 0.5) / len(signals))
        direction = "RISING" if trend > 0 else "FALLING" if trend < 0 else "FLAT"

        graph = nx.DiGraph()
        for signal in signals:
            graph.add_node(str(signal.signal_id), domain=signal.domain, score=signal.anomaly_score)
        for link in propagation_links:
            graph.add_edge(link.source_signal_id, link.target_signal_id, lag=link.lag, evidence_id=link.evidence_id)

        domain_pairs = {
            tuple(sorted((graph.nodes[a]["domain"], graph.nodes[b]["domain"])))
            for a, b in graph.edges
            if graph.nodes[a]["domain"] != graph.nodes[b]["domain"]
        }
        distinct_domains = len(pattern.domains)
        possible = distinct_domains * (distinct_domains - 1) / 2
        propagation = min(1.0, len(domain_pairs) / possible) if possible else 0.0
        cascade = min(1.0, persistence * pattern.coherence * propagation)
        provenance = tuple(
            dict.fromkeys(
                pattern.provenance
                + tuple(p for signal in signals for p in signal.provenance)
                + tuple(link.evidence_id for link in propagation_links)
            )
        )
        return Trajectory(
            str(uuid4()),
            pattern.pattern_id,
            direction,
            persistence,
            acceleration,
            propagation,
            cascade,
            regime,
            provenance,
        )


class AlertEngine:
    def build(self, trajectory: Trajectory, *, event_ids: tuple[str, ...] = (), signal_ids: tuple[str, ...] = (), forecasts: tuple[str, ...] = (), data_process_change: bool = False, data_process_reasons: tuple[str, ...] = ()) -> Alert:
        raw = min(1.0, max(0.0, 0.5 * trajectory.persistence + 0.3 * trajectory.cascade_score + 0.2 * trajectory.propagation))
        uncertainty = min(1.0, 1.0 - trajectory.persistence * max(trajectory.propagation, 0.1))
        rationale = [f"trajectory={trajectory.direction}", f"regime={trajectory.regime}", f"cascade_score={trajectory.cascade_score:.4f}", f"domain_propagation={trajectory.propagation:.4f}"]
        if data_process_change:
            return Alert(str(uuid4()), "DATA_QUALITY_REVIEW", 0.0, tuple(rationale + list(data_process_reasons)), event_ids, signal_ids, forecasts, 1.0, trajectory.provenance)
        level = "CRITICAL" if raw >= 0.85 and uncertainty < 0.35 else "DANGER" if raw >= 0.70 else "WARNING" if raw >= 0.50 else "ATTENTION" if raw >= 0.30 else "BASELINE"
        return Alert(str(uuid4()), level, raw, tuple(rationale), event_ids, signal_ids, forecasts, uncertainty, trajectory.provenance)


__all__ = ["AlertEngine", "EventEngine", "Pattern", "PatternEngine", "PropagationLink", "SignalEngine", "Trajectory", "TrajectoryEngine"]
