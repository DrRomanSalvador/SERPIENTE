"""Cross-repository scientific contracts for SERPIENTE prediction records.

These contracts preserve temporal identity, uncertainty and benchmark lineage.
They do not assert prospective validity or causal validity merely by validation of
Python objects.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class Identifiability(StrEnum):
    IDENTIFIABLE = "IDENTIFIABLE"
    PARTIALLY_IDENTIFIABLE = "PARTIALLY_IDENTIFIABLE"
    NON_IDENTIFIABLE = "NON_IDENTIFIABLE"
    UNKNOWN = "UNKNOWN"


class BenchmarkFamily(StrEnum):
    PERSISTENCE = "PERSISTENCE"
    SEASONAL_BASELINE = "SEASONAL_BASELINE"
    MEAN = "MEAN"
    TREND = "TREND"
    SIMPLE_AR = "SIMPLE_AR"
    REGULARIZED_MODEL = "REGULARIZED_MODEL"
    HIERARCHICAL_MODEL = "HIERARCHICAL_MODEL"
    DOCUMENTED_EXPERT_FORECAST = "DOCUMENTED_EXPERT_FORECAST"


@dataclass(frozen=True, slots=True)
class PointInTimePredictionContract:
    prediction_id: str
    information_cutoff: str
    observation_vintage: str
    feature_availability: tuple[tuple[str, str], ...]
    forecast_origin: str
    forecast_horizon: str
    model_version: str
    target_definition: str
    outcome_definition: str
    point_in_time_fingerprint: str
    provenance: tuple[str, ...]
    identifiability: Identifiability = Identifiability.UNKNOWN

    def __post_init__(self) -> None:
        required = (
            self.prediction_id,
            self.information_cutoff,
            self.observation_vintage,
            self.forecast_origin,
            self.forecast_horizon,
            self.model_version,
            self.target_definition,
            self.outcome_definition,
            self.point_in_time_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("prediction contract is incomplete")
        if not self.feature_availability or not self.provenance:
            raise ValueError("prediction requires feature availability and provenance")


@dataclass(frozen=True, slots=True)
class BenchmarkContract:
    benchmark_id: str
    family: BenchmarkFamily
    target_definition: str
    horizon: str
    applicability: str
    exclusion_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.benchmark_id or not self.target_definition or not self.horizon:
            raise ValueError("benchmark identity/target/horizon are required")
        if self.applicability == "EXCLUDED" and not self.exclusion_reason:
            raise ValueError("excluded benchmarks require an explicit reason")


@dataclass(frozen=True, slots=True)
class PredictionMetricDefinition:
    metric_id: str
    question: str
    detects_failure: str
    does_not_detect: str

    def __post_init__(self) -> None:
        if not all((self.metric_id, self.question, self.detects_failure, self.does_not_detect)):
            raise ValueError("prediction metric definition is incomplete")


@dataclass(frozen=True, slots=True)
class ModelChangeGate:
    model_id: str
    current_version: str
    proposed_version: str
    training_data_vintage: str
    validation_data_vintage: str
    benchmark_ids: tuple[str, ...]
    validation_passed: bool
    approval_record: str | None
    deployment_approved: bool
    rollback_condition: str

    def __post_init__(self) -> None:
        if not self.benchmark_ids or not self.rollback_condition:
            raise ValueError("model change requires benchmarks and rollback condition")
        if self.deployment_approved and (not self.validation_passed or not self.approval_record):
            raise ValueError("deployment cannot be approved without validation and approval")


@dataclass(frozen=True, slots=True)
class ObservationProcessDescriptor:
    variable_id: str
    definition: str
    measurement_process: str
    denominator: str
    coverage: str
    bias: str
    measurement_error: str
    temporal_resolution: str
    source: str

    def __post_init__(self) -> None:
        if not all((self.variable_id, self.definition, self.measurement_process, self.denominator, self.coverage, self.temporal_resolution, self.source)):
            raise ValueError("observation process descriptor is incomplete")


def valid_probability(value: float) -> bool:
    return isfinite(value) and 0.0 <= value <= 1.0


__all__ = [
    "BenchmarkContract",
    "BenchmarkFamily",
    "Identifiability",
    "ModelChangeGate",
    "ObservationProcessDescriptor",
    "PointInTimePredictionContract",
    "PredictionMetricDefinition",
    "valid_probability",
]
