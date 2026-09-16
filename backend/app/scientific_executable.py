"""Executable scientific primitives for F-K.

This module turns the already-defined scientific requirements into typed,
testable objects and deterministic numerical primitives. It deliberately does
not claim prospective, causal, or operational validity.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from math import isfinite, sqrt
from typing import Callable, Mapping, Sequence

import numpy as np


class EpistemicStatus(StrEnum):
    IMPLEMENTED_NOT_VALIDATED = "IMPLEMENTED_NOT_VALIDATED"
    RETROSPECTIVELY_EVALUATED = "RETROSPECTIVELY_EVALUATED"
    PROSPECTIVELY_VALIDATED = "PROSPECTIVELY_VALIDATED"


class VariableKind(StrEnum):
    OBSERVED = "observed"
    MEASURED = "measured"
    INFERRED = "inferred"
    LATENT = "latent"
    PREDICTED = "predicted"


@dataclass(frozen=True, slots=True)
class ScientificVariable:
    variable_id: str
    kind: VariableKind
    unit: str
    definition: str
    provenance: tuple[str, ...]
    valid_from: datetime | None = None
    valid_to: datetime | None = None

    def __post_init__(self) -> None:
        if not all((self.variable_id.strip(), self.unit.strip(), self.definition.strip())):
            raise ValueError("scientific variable identity/unit/definition are required")
        if not self.provenance:
            raise ValueError("scientific variable requires provenance")
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("validity window is inverted")


@dataclass(frozen=True, slots=True)
class LatentState:
    state_id: str
    timestamp: datetime
    values: tuple[float, ...]
    uncertainty: tuple[float, ...]
    model_version: str
    provenance: tuple[str, ...]
    status: EpistemicStatus = EpistemicStatus.IMPLEMENTED_NOT_VALIDATED

    def __post_init__(self) -> None:
        if not self.state_id or not self.model_version or not self.provenance:
            raise ValueError("latent state requires identity, model version and provenance")
        if len(self.values) != len(self.uncertainty) or not self.values:
            raise ValueError("state and uncertainty dimensions must match")
        if any(not isfinite(x) or x < 0 for x in self.uncertainty):
            raise ValueError("state uncertainty must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class ObservationProcess:
    process_id: str
    measurement: str
    reporting: str
    denominator: str
    ascertainment: str
    coverage: str
    latency: str
    revision: str
    missingness: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        fields = (self.process_id, self.measurement, self.reporting, self.denominator,
                  self.ascertainment, self.coverage, self.latency, self.revision,
                  self.missingness)
        if any(not field.strip() for field in fields) or not self.provenance:
            raise ValueError("observation process is incomplete")


@dataclass(frozen=True, slots=True)
class StateTransition:
    previous: tuple[float, ...]
    action: tuple[float, ...]
    exogenous: tuple[float, ...]
    next_state: tuple[float, ...]
    process_noise: tuple[float, ...]
    model_version: str

    def __post_init__(self) -> None:
        if len(self.previous) != len(self.next_state) or len(self.previous) != len(self.process_noise):
            raise ValueError("state transition dimensions must match")
        if any(not isfinite(x) for x in (*self.previous, *self.next_state, *self.process_noise)):
            raise ValueError("state transition values must be finite")


def linear_state_transition(
    state: Sequence[float],
    action: Sequence[float],
    exogenous: Sequence[float],
    state_matrix: np.ndarray,
    action_matrix: np.ndarray,
    exogenous_matrix: np.ndarray,
    process_noise: Sequence[float] | None = None,
) -> StateTransition:
    s = np.asarray(state, dtype=float)
    a = np.asarray(action, dtype=float)
    u = np.asarray(exogenous, dtype=float)
    w = np.zeros_like(s) if process_noise is None else np.asarray(process_noise, dtype=float)
    A = np.asarray(state_matrix, dtype=float)
    B = np.asarray(action_matrix, dtype=float)
    G = np.asarray(exogenous_matrix, dtype=float)
    if A.shape != (s.size, s.size) or B.shape != (s.size, a.size) or G.shape != (s.size, u.size):
        raise ValueError("transition matrices have incompatible dimensions")
    nxt = A @ s + B @ a + G @ u + w
    return StateTransition(tuple(s), tuple(a), tuple(u), tuple(nxt), tuple(w), "linear-state-v1")


def observation_projection(
    state: Sequence[float],
    measurement_matrix: np.ndarray,
    observation_bias: Sequence[float] | None = None,
) -> np.ndarray:
    s = np.asarray(state, dtype=float)
    H = np.asarray(measurement_matrix, dtype=float)
    if H.ndim != 2 or H.shape[1] != s.size:
        raise ValueError("measurement matrix has incompatible dimensions")
    b = np.zeros(H.shape[0]) if observation_bias is None else np.asarray(observation_bias, dtype=float)
    if b.shape != (H.shape[0],):
        raise ValueError("observation bias has incompatible dimensions")
    return H @ s + b


@dataclass(frozen=True, slots=True)
class LaggedRelation:
    relation_id: str
    origin: str
    destination: str
    direction: str
    lags: tuple[int, ...]
    spatial_scale: str
    temporal_scale: str
    mechanism: str
    evidence_ids: tuple[str, ...]
    causal_status: str
    measurement_dependency: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.relation_id or not self.origin or not self.destination:
            raise ValueError("relation identity is incomplete")
        if any(lag < 0 for lag in self.lags):
            raise ValueError("lags must be non-negative")
        if not self.provenance:
            raise ValueError("relation requires provenance")


def lagged_values(values: Sequence[float], lag: int) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if lag < 0:
        raise ValueError("lag must be non-negative")
    if lag >= x.size:
        return np.asarray([], dtype=float)
    return x[: x.size - lag]


def distributed_lag(values: Sequence[float], lags: Sequence[int], weights: Sequence[float]) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    ls = tuple(int(v) for v in lags)
    ws = np.asarray(weights, dtype=float)
    if len(ls) != ws.size or not ls or any(v < 0 for v in ls):
        raise ValueError("lags and weights must be non-empty and aligned")
    if not np.all(np.isfinite(ws)):
        raise ValueError("lag weights must be finite")
    horizon = x.size - max(ls)
    if horizon <= 0:
        return np.asarray([], dtype=float)
    return np.column_stack([x[max(ls) - lag : max(ls) - lag + horizon] for lag in ls]) @ ws


@dataclass(frozen=True, slots=True)
class DynamicCoupling:
    origin: str
    destination: str
    timestamp: datetime
    coefficient: float
    uncertainty: float
    estimation_method: str
    valid_from: datetime
    valid_to: datetime | None
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isfinite(self.coefficient) or not isfinite(self.uncertainty) or self.uncertainty < 0:
            raise ValueError("coupling coefficient/uncertainty invalid")
        if self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("coupling validity window is inverted")
        if not self.provenance:
            raise ValueError("coupling requires provenance")


@dataclass(frozen=True, slots=True)
class UncertaintyDecomposition:
    measurement: float = 0.0
    parameter: float = 0.0
    model: float = 0.0
    process: float = 0.0
    observation: float = 0.0
    structural: float = 0.0
    forecast: float = 0.0
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        values = (self.measurement, self.parameter, self.model, self.process,
                  self.observation, self.structural, self.forecast)
        if any(not isfinite(v) or v < 0 for v in values):
            raise ValueError("uncertainty components must be finite and non-negative")
        if not self.provenance:
            raise ValueError("uncertainty requires provenance")

    @property
    def total_variance_proxy(self) -> float:
        return sum((self.measurement, self.parameter, self.model, self.process,
                    self.observation, self.structural, self.forecast))


@dataclass(frozen=True, slots=True)
class ForecastEvaluation:
    metric: str
    baseline_score: float
    candidate_score: float
    direction: str
    delta: float
    calibration_status: str
    validation_status: EpistemicStatus

    @property
    def candidate_improves(self) -> bool:
        return self.delta > 0 if self.direction == "HIGHER_IS_BETTER" else self.delta < 0


def brier_score(y_true: Sequence[int | float], probability: Sequence[float]) -> float:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(probability, dtype=float)
    if y.shape != p.shape or y.size == 0 or np.any((p < 0) | (p > 1)):
        raise ValueError("Brier inputs must be aligned non-empty probabilities in [0,1]")
    return float(np.mean((p - y) ** 2))


def log_loss(y_true: Sequence[int | float], probability: Sequence[float], eps: float = 1e-15) -> float:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(probability, dtype=float)
    if y.shape != p.shape or y.size == 0 or np.any((p < 0) | (p > 1)):
        raise ValueError("log-loss inputs must be aligned probabilities in [0,1]")
    q = np.clip(p, eps, 1.0 - eps)
    return float(-np.mean(y * np.log(q) + (1.0 - y) * np.log1p(-q)))


def crps_ensemble(observed: Sequence[float], ensemble: Sequence[Sequence[float]]) -> float:
    y = np.asarray(observed, dtype=float)
    e = np.asarray(ensemble, dtype=float)
    if e.ndim != 2 or y.ndim != 1 or e.shape[0] != y.size or e.shape[1] == 0:
        raise ValueError("CRPS ensemble dimensions are invalid")
    term1 = np.mean(np.abs(e - y[:, None]), axis=1)
    term2 = 0.5 * np.mean(np.abs(e[:, :, None] - e[:, None, :]), axis=(1, 2))
    return float(np.mean(term1 - term2))


def interval_coverage(observed: Sequence[float], lower: Sequence[float], upper: Sequence[float]) -> float:
    y, lo, hi = map(lambda x: np.asarray(x, dtype=float), (observed, lower, upper))
    if not (y.shape == lo.shape == hi.shape) or y.size == 0 or np.any(lo > hi):
        raise ValueError("interval inputs are invalid")
    return float(np.mean((y >= lo) & (y <= hi)))


def compare_forecasts(
    y_true: Sequence[float],
    baseline: Sequence[float],
    candidate: Sequence[float],
    *,
    metric: Callable[[Sequence[float], Sequence[float]], float],
    metric_name: str,
    direction: str = "LOWER_IS_BETTER",
    calibration_status: str = "NOT_ASSESSED",
    validation_status: EpistemicStatus = EpistemicStatus.IMPLEMENTED_NOT_VALIDATED,
) -> ForecastEvaluation:
    b = metric(y_true, baseline)
    c = metric(y_true, candidate)
    return ForecastEvaluation(metric_name, b, c, direction, c - b, calibration_status, validation_status)


def persistence_forecast(values: Sequence[float], horizon: int = 1) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.size == 0 or horizon < 1:
        raise ValueError("persistence requires non-empty values and positive horizon")
    return np.repeat(x[-1], horizon)


def seasonal_mean_forecast(values: Sequence[float], period: int, horizon: int = 1) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.size == 0 or period < 1 or horizon < 1:
        raise ValueError("seasonal mean inputs are invalid")
    window = x[-period:]
    return np.repeat(float(np.mean(window)), horizon)


def linear_trend_forecast(values: Sequence[float], horizon: int = 1) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.size < 2 or horizon < 1:
        raise ValueError("trend requires at least two observations")
    t = np.arange(x.size, dtype=float)
    slope, intercept = np.polyfit(t, x, 1)
    return intercept + slope * np.arange(x.size, x.size + horizon, dtype=float)


def rolling_change(values: Sequence[float], window: int) -> Mapping[str, float]:
    x = np.asarray(values, dtype=float)
    if window < 2 or x.size < 2 * window:
        raise ValueError("change detector requires two complete windows")
    a, b = x[-2 * window : -window], x[-window:]
    return {
        "delta_mean": float(np.mean(b) - np.mean(a)),
        "delta_variance": float(np.var(b, ddof=1) - np.var(a, ddof=1)),
        "delta_autocorrelation": float(_lag1_autocorrelation(b) - _lag1_autocorrelation(a)),
    }


def _lag1_autocorrelation(x: np.ndarray) -> float:
    if x.size < 3:
        return float("nan")
    a, b = x[:-1], x[1:]
    sa, sb = np.std(a), np.std(b)
    if sa == 0 or sb == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


@dataclass(frozen=True, slots=True)
class AlertContract:
    alert_id: str
    issued_at: datetime
    information_cutoff: datetime
    phenomenon: str
    geographic_scope: str
    population_scope: str
    horizon: str
    trigger: str
    base_rate: float | None
    predictive_distribution: str
    calibration_status: str
    main_evidence: tuple[str, ...]
    alternative_explanations: tuple[str, ...]
    measurement_change_check: str
    uncertainty: str
    decision_owner: str
    reversible_actions: tuple[str, ...]
    potential_harms: tuple[str, ...]
    escalation_rule: str
    expiry: datetime
    outcome_to_capture: str

    def __post_init__(self) -> None:
        if self.issued_at < self.information_cutoff:
            raise ValueError("alert cannot be issued before its information cutoff")
        if self.expiry <= self.issued_at:
            raise ValueError("alert expiry must follow issuance")
        if self.base_rate is not None and not 0 <= self.base_rate <= 1:
            raise ValueError("base rate must be in [0,1]")
        required = (self.alert_id, self.phenomenon, self.horizon, self.trigger,
                    self.predictive_distribution, self.calibration_status,
                    self.measurement_change_check, self.uncertainty, self.decision_owner,
                    self.escalation_rule, self.outcome_to_capture)
        if any(not value.strip() for value in required) or not self.main_evidence or not self.alternative_explanations:
            raise ValueError("alert contract is incomplete")


class InterventionStatus(StrEnum):
    NONE = "none"
    PLANNED = "planned"
    EXECUTED = "executed"


@dataclass(frozen=True, slots=True)
class InterventionRecord:
    intervention_id: str
    status: InterventionStatus
    action_time: datetime | None
    exposed_population: str
    action_definition: str
    expected_outcome: str
    observed_outcome_id: str | None
    counterfactual_requirement: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.intervention_id or not self.exposed_population or not self.action_definition:
            raise ValueError("intervention identity/action/exposure are required")
        if self.status == InterventionStatus.EXECUTED and self.action_time is None:
            raise ValueError("executed intervention requires action time")
        if not self.provenance:
            raise ValueError("intervention requires provenance")


class OutcomeFailure(StrEnum):
    PREDICTION = "prediction_failure"
    DECISION = "decision_failure"
    EXECUTION = "execution_failure"
    INTERVENTION = "intervention_failure"
    OBSERVATION = "observation_failure"


@dataclass(frozen=True, slots=True)
class OutcomeEvaluation:
    prediction_id: str
    outcome_id: str
    failure_class: OutcomeFailure | None
    observed_value: str
    outcome_definition: str
    ascertainment_status: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all((self.prediction_id, self.outcome_id, self.observed_value, self.outcome_definition, self.ascertainment_status)):
            raise ValueError("outcome evaluation is incomplete")
        if not self.provenance:
            raise ValueError("outcome evaluation requires provenance")


__all__ = [
    "AlertContract", "DynamicCoupling", "EpistemicStatus", "ForecastEvaluation",
    "InterventionRecord", "InterventionStatus", "LaggedRelation", "LatentState",
    "ObservationProcess", "OutcomeEvaluation", "OutcomeFailure", "ScientificVariable",
    "StateTransition", "UncertaintyDecomposition", "VariableKind", "brier_score",
    "compare_forecasts", "crps_ensemble", "distributed_lag", "interval_coverage",
    "lagged_values", "linear_state_transition", "linear_trend_forecast",
    "log_loss", "observation_projection", "persistence_forecast", "rolling_change",
    "seasonal_mean_forecast",
]
