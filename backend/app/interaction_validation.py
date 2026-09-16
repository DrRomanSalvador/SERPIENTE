"""Scientific contracts for validating cross-system predictive interactions.

This module does not create a second forecasting engine. It evaluates whether an
explicit interaction adds incremental prospective/PIT-valid predictive
information beyond a target system's baseline model.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log
from typing import Sequence


_EVIDENCE_LEVELS = {f"E{i}" for i in range(9)}
_CAUSAL_STATUSES = {"UNKNOWN", "OBSERVATIONAL", "PREDICTIVE", "MECHANISTIC", "CAUSAL_HYPOTHESIS", "CAUSALLY_SUPPORTED", "INTERVENTION_SUPPORTED"}


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class InteractionSpec:
    """One scientifically declared directed interaction hypothesis."""

    source_system: str
    target_system: str
    direction: str
    lag: str
    mechanism: str
    evidence_level: str = "E0"
    causal_status: str = "UNKNOWN"
    spatial_scale: str = "UNSPECIFIED"
    measurement_dependence: str = "UNKNOWN"

    def __post_init__(self) -> None:
        for name in ("source_system", "target_system", "direction", "lag", "mechanism"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} is required")
        if self.source_system == self.target_system:
            raise ValueError("source_system and target_system must differ")
        if self.evidence_level not in _EVIDENCE_LEVELS:
            raise ValueError("evidence_level must be E0..E8")
        if self.causal_status not in _CAUSAL_STATUSES:
            raise ValueError("unsupported causal_status")
        if self.measurement_dependence not in {"UNKNOWN", "INDEPENDENT", "SHARED_SOURCE", "SAME_PHENOMENON", "PROCESS_DEPENDENT"}:
            raise ValueError("unsupported measurement_dependence")


@dataclass(frozen=True, slots=True)
class PredictionRecord:
    origin_time: datetime
    available_at: datetime
    outcome_time: datetime
    probability: float

    def __post_init__(self) -> None:
        origin = _utc(self.origin_time, "origin_time")
        available = _utc(self.available_at, "available_at")
        outcome = _utc(self.outcome_time, "outcome_time")
        if available > origin:
            raise ValueError("prediction was not available at its origin")
        if outcome <= origin:
            raise ValueError("outcome_time must be after prediction origin")
        if not isfinite(self.probability) or not 0 <= self.probability <= 1:
            raise ValueError("probability must be finite and in [0,1]")
        object.__setattr__(self, "origin_time", origin)
        object.__setattr__(self, "available_at", available)
        object.__setattr__(self, "outcome_time", outcome)


@dataclass(frozen=True, slots=True)
class IncrementalPredictiveValue:
    interaction_spec: InteractionSpec
    observations: int
    temporal_order_valid: bool
    pit_valid: bool
    baseline_brier: float
    interaction_brier: float
    brier_improvement: float
    baseline_logloss: float
    interaction_logloss: float
    logloss_improvement: float


def _validate_records(records: Sequence[PredictionRecord], outcomes: Sequence[int]) -> None:
    if not records or len(records) != len(outcomes):
        raise ValueError("records and outcomes must be non-empty and have equal length")
    origins = [record.origin_time for record in records]
    if any(origins[i] >= origins[i + 1] for i in range(len(origins) - 1)):
        raise ValueError("prediction origins must be strictly increasing")
    if any(outcome not in {0, 1} for outcome in outcomes):
        raise ValueError("outcomes must be binary")


def _brier(records: Sequence[PredictionRecord], outcomes: Sequence[int]) -> float:
    return sum((record.probability - outcome) ** 2 for record, outcome in zip(records, outcomes)) / len(records)


def _logloss(records: Sequence[PredictionRecord], outcomes: Sequence[int]) -> float:
    total = 0.0
    for record, outcome in zip(records, outcomes):
        p = min(1.0 - 1e-15, max(1e-15, record.probability))
        total -= outcome * log(p) + (1 - outcome) * log(1 - p)
    return total / len(records)


def compare_incremental_predictive_value(
    interaction: InteractionSpec,
    baseline: Sequence[PredictionRecord],
    interaction_model: Sequence[PredictionRecord],
    outcomes: Sequence[int],
) -> IncrementalPredictiveValue:
    """Compare a target-only baseline with an interaction-augmented forecast.

    The comparison is deliberately prospective/PIT-oriented: every prediction
    must have been available by its origin, origins must be ordered, and the
    realized outcome must occur after the origin. No causal claim is inferred.
    """
    _validate_records(baseline, outcomes)
    _validate_records(interaction_model, outcomes)
    if len(baseline) != len(interaction_model):
        raise ValueError("baseline and interaction predictions must be paired")
    if any(a.origin_time != b.origin_time or a.outcome_time != b.outcome_time for a, b in zip(baseline, interaction_model)):
        raise ValueError("baseline and interaction predictions must share origins and outcome times")
    pit_valid = all(record.available_at <= record.origin_time < record.outcome_time for record in (*baseline, *interaction_model))
    return IncrementalPredictiveValue(
        interaction_spec=interaction,
        observations=len(outcomes),
        temporal_order_valid=True,
        pit_valid=pit_valid,
        baseline_brier=_brier(baseline, outcomes),
        interaction_brier=_brier(interaction_model, outcomes),
        brier_improvement=_brier(baseline, outcomes) - _brier(interaction_model, outcomes),
        baseline_logloss=_logloss(baseline, outcomes),
        interaction_logloss=_logloss(interaction_model, outcomes),
        logloss_improvement=_logloss(baseline, outcomes) - _logloss(interaction_model, outcomes),
    )


__all__ = ["IncrementalPredictiveValue", "InteractionSpec", "PredictionRecord", "compare_incremental_predictive_value"]
