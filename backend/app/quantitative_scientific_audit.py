"""Quantitative scientific-audit primitives.

These objects force explicit treatment of population, observation, denominator,
temporal semantics, identification, uncertainty, bias, alternatives,
falsification and validation. They encode scientific structure; they do not
claim that the represented phenomenon, model or causal effect is true.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Sequence

import numpy as np


class InferenceType(StrEnum):
    DESCRIPTIVE = "DESCRIPTIVE"
    ASSOCIATIONAL = "ASSOCIATIONAL"
    PREDICTIVE = "PREDICTIVE"
    MECHANISTIC = "MECHANISTIC"
    CAUSAL = "CAUSAL"
    DECISIONAL = "DECISIONAL"


class IdentificationStatus(StrEnum):
    NOT_ASSESSED = "NOT_ASSESSED"
    IDENTIFIED = "IDENTIFIED"
    PARTIALLY_IDENTIFIED = "PARTIALLY_IDENTIFIED"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"


@dataclass(frozen=True, slots=True)
class QuantitativeMethodAudit:
    method_id: str
    phenomenon: str
    scientific_question: str
    target_population: str
    outcome_definition: str
    predictor_definitions: tuple[str, ...]
    units: tuple[str, ...]
    domain: str
    assumptions: tuple[str, ...]
    identification: IdentificationStatus
    estimation: str
    uncertainty: tuple[str, ...]
    sensitivity: tuple[str, ...]
    robustness: tuple[str, ...]
    validation: tuple[str, ...]
    benchmarks: tuple[str, ...]
    falsification: tuple[str, ...]
    inference_type: InferenceType
    capability_not_authorized: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        required = (self.method_id, self.phenomenon, self.scientific_question,
                    self.target_population, self.outcome_definition, self.domain,
                    self.estimation)
        if any(not x.strip() for x in required):
            raise ValueError("quantitative audit identity/question fields are required")
        if not self.predictor_definitions or not self.units or not self.assumptions:
            raise ValueError("quantitative audit requires variables, units and assumptions")
        if not self.uncertainty or not self.benchmarks or not self.falsification:
            raise ValueError("quantitative audit requires uncertainty, benchmarks and falsification")
        if not self.validation or not self.provenance or not self.capability_not_authorized:
            raise ValueError("quantitative audit requires validation, provenance and capability boundary")


@dataclass(frozen=True, slots=True)
class DenominatorSpec:
    denominator_id: str
    target_population: str
    exposed_population: str
    observed_population: str
    eligible_population: str
    time_at_risk: str
    spatial_scope: str
    mobility_assumption: str
    ascertainment_process: str
    numerator_source: str
    denominator_source: str
    uncertainty: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        fields = (self.denominator_id, self.target_population, self.exposed_population,
                  self.observed_population, self.eligible_population, self.time_at_risk,
                  self.spatial_scope, self.mobility_assumption, self.ascertainment_process,
                  self.numerator_source, self.denominator_source, self.uncertainty)
        if any(not x.strip() for x in fields) or not self.provenance:
            raise ValueError("denominator specification is incomplete")


@dataclass(frozen=True, slots=True)
class ObservationModelSpec:
    model_id: str
    latent_state: str
    observed_variable: str
    observation_process: str
    denominator: str
    reporting_process: str
    coverage_process: str
    equation: str
    failure_modes: tuple[str, ...]
    diagnostics: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        fields = (self.model_id, self.latent_state, self.observed_variable,
                  self.observation_process, self.denominator, self.reporting_process,
                  self.coverage_process, self.equation)
        if any(not x.strip() for x in fields) or not self.failure_modes or not self.diagnostics or not self.provenance:
            raise ValueError("observation model requires process, failure modes and diagnostics")


@dataclass(frozen=True, slots=True)
class BiasAudit:
    bias_id: str
    bias_type: str
    presence: str
    plausibility: str
    direction: str
    magnitude: str
    mitigation: str
    residual_uncertainty: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        fields = (self.bias_id, self.bias_type, self.presence, self.plausibility,
                  self.direction, self.magnitude, self.mitigation, self.residual_uncertainty)
        if any(not x.strip() for x in fields) or not self.provenance:
            raise ValueError("bias audit is incomplete")


@dataclass(frozen=True, slots=True)
class SensitivityScenario:
    scenario_id: str
    assumption_changed: str
    alternative_specification: str
    estimand_or_target: str
    expected_discriminating_observation: str
    falsification_condition: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        fields = (self.scenario_id, self.assumption_changed, self.alternative_specification,
                  self.estimand_or_target, self.expected_discriminating_observation,
                  self.falsification_condition)
        if any(not x.strip() for x in fields) or not self.provenance:
            raise ValueError("sensitivity scenario is incomplete")


@dataclass(frozen=True, slots=True)
class EvidenceDependency:
    evidence_id: str
    source_id: str
    dataset_id: str
    author_group_id: str
    method_family_id: str
    measurement_process_id: str
    institutional_process_id: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        fields = (self.evidence_id, self.source_id, self.dataset_id, self.author_group_id,
                  self.method_family_id, self.measurement_process_id, self.institutional_process_id)
        if any(not x.strip() for x in fields) or not self.provenance:
            raise ValueError("evidence dependency identity is incomplete")


def evidence_independence_matrix(items: Sequence[EvidenceDependency]) -> np.ndarray:
    """Return a conservative dependency matrix: 1 means shared evidence lineage."""
    n = len(items)
    matrix = np.zeros((n, n), dtype=int)
    fields = ("dataset_id", "author_group_id", "method_family_id", "measurement_process_id", "institutional_process_id")
    for i, left in enumerate(items):
        for j, right in enumerate(items):
            matrix[i, j] = int(i == j or any(getattr(left, f) == getattr(right, f) for f in fields))
    return matrix


def brier_skill_score(y_true: Sequence[int | float], baseline_probability: Sequence[float], candidate_probability: Sequence[float]) -> float:
    """Relative improvement over a baseline; positive means lower Brier loss."""
    y = np.asarray(y_true, dtype=float)
    b = np.asarray(baseline_probability, dtype=float)
    c = np.asarray(candidate_probability, dtype=float)
    if y.shape != b.shape or y.shape != c.shape or y.size == 0:
        raise ValueError("Brier skill inputs must be aligned and non-empty")
    if np.any((b < 0) | (b > 1) | (c < 0) | (c > 1)):
        raise ValueError("probabilities must lie in [0,1]")
    lb = float(np.mean((b - y) ** 2))
    lc = float(np.mean((c - y) ** 2))
    if lb == 0:
        return 0.0 if lc == 0 else float("-inf")
    return (lb - lc) / lb


def calibration_in_the_large(y_true: Sequence[int | float], probability: Sequence[float]) -> float:
    """Observed event rate minus mean predicted probability."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(probability, dtype=float)
    if y.shape != p.shape or y.size == 0 or np.any((p < 0) | (p > 1)):
        raise ValueError("calibration inputs are invalid")
    return float(np.mean(y) - np.mean(p))


def interval_width(lower: Sequence[float], upper: Sequence[float]) -> float:
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    if lo.shape != hi.shape or lo.size == 0 or np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo > hi):
        raise ValueError("prediction interval bounds are invalid")
    return float(np.mean(hi - lo))


def lagged_pair(values: Sequence[float], lag: int) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(values, dtype=float)
    if lag < 0 or lag >= x.size:
        raise ValueError("lag must be non-negative and shorter than the series")
    return x[:-lag or None], x[lag:]


__all__ = [
    "BiasAudit", "DenominatorSpec", "EvidenceDependency", "IdentificationStatus",
    "InferenceType", "ObservationModelSpec", "QuantitativeMethodAudit",
    "SensitivityScenario", "brier_skill_score", "calibration_in_the_large",
    "evidence_independence_matrix", "interval_width", "lagged_pair",
]
