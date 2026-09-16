"""Execute bounded scientific work against concrete SERPIENTE runtime objects.

The executor performs only analyses supported by the information carried by the
runtime object. It records inconclusive or externally blocked outcomes instead
of promoting epistemic status. This closes the runtime finding -> work -> result
boundary without pretending that a single runtime object constitutes validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .contracts import Forecast, Observation, Signal
from .scientific_discovery_engine import ScientificWork


class ExecutionOutcome(StrEnum):
    EXECUTED = "EXECUTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REJECTED = "REJECTED"
    BLOCKED_EXTERNAL = "BLOCKED_EXTERNAL"


@dataclass(frozen=True, slots=True)
class ScientificWorkResult:
    work_id: str
    runtime_id: str
    outcome: ExecutionOutcome
    finding: str
    evidence: tuple[str, ...]
    epistemic_state: str
    new_work_required: bool
    capability_not_authorized: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.work_id or not self.runtime_id or not self.finding:
            raise ValueError("execution result identity and finding are required")
        if not self.evidence or not self.provenance:
            raise ValueError("execution result requires evidence and provenance")
        if not self.capability_not_authorized:
            raise ValueError("execution result requires capability boundary")


def _runtime_id(obj: Observation | Signal | Forecast) -> str:
    if isinstance(obj, Observation):
        return str(obj.observation_id)
    if isinstance(obj, Signal):
        return str(obj.signal_id)
    return str(obj.forecast_id)


def _base_result(work: ScientificWork, obj: Observation | Signal | Forecast, outcome: ExecutionOutcome, finding: str, evidence: tuple[str, ...], state: str, new_work: bool) -> ScientificWorkResult:
    return ScientificWorkResult(
        work_id=work.work_id,
        runtime_id=_runtime_id(obj),
        outcome=outcome,
        finding=finding,
        evidence=evidence,
        epistemic_state=state,
        new_work_required=new_work,
        capability_not_authorized=work.capability_not_authorized,
        provenance=tuple(dict.fromkeys((*work.provenance, f"runtime:{_runtime_id(obj)}"))),
    )


def execute_scientific_work(work: ScientificWork, obj: Observation | Signal | Forecast) -> ScientificWorkResult:
    """Execute the strongest analysis justified by one concrete runtime object."""
    runtime_id = _runtime_id(obj)

    if isinstance(obj, Observation):
        temporal_ok = obj.event_time <= obj.publication_time <= obj.acquisition_time
        if not temporal_ok:
            return _base_result(
                work, obj, ExecutionOutcome.REJECTED,
                "observation temporal ordering is invalid",
                (f"event_time={obj.event_time.isoformat()}", f"publication_time={obj.publication_time.isoformat()}", f"acquisition_time={obj.acquisition_time.isoformat()}"),
                "REJECTED",
                True,
            )
        finding = (
            "observation contract is temporally coherent and provenance-bearing; "
            "a single observation cannot distinguish phenomenon drift from measurement, "
            "reporting, denominator, coverage, or ascertainment drift"
        )
        return _base_result(
            work, obj, ExecutionOutcome.INCONCLUSIVE, finding,
            (f"source={obj.source_id}", f"dataset={obj.dataset_id}", f"variable={obj.variable_id}", f"revision={obj.revision}", f"known_at_acquisition={obj.known_at(obj.acquisition_time)}"),
            "OBSERVATION",
            True,
        )

    if isinstance(obj, Signal):
        finding = (
            "signal is numerically well-formed and provenance-bearing, but the current "
            "Signal contract contains no event timestamp; temporal precedence, lead time, "
            "and change-point claims are therefore not identifiable from this object"
        )
        return _base_result(
            work, obj, ExecutionOutcome.INCONCLUSIVE, finding,
            (f"anomaly_score={obj.anomaly_score}", f"trend={obj.trend}", f"acceleration={obj.acceleration}", f"volatility={obj.volatility}"),
            "SIGNAL",
            True,
        )

    probability_ok = 0.0 <= obj.probability <= 1.0
    interval_ok = obj.lower <= obj.upper
    pit_present = bool(obj.point_in_time_fingerprint)
    if not (probability_ok and interval_ok and pit_present):
        return _base_result(
            work, obj, ExecutionOutcome.REJECTED,
            "forecast contract fails a structural validity check",
            (f"probability_ok={probability_ok}", f"interval_ok={interval_ok}", f"pit_present={pit_present}"),
            "REJECTED",
            True,
        )
    return _base_result(
        work, obj, ExecutionOutcome.BLOCKED_EXTERNAL,
        "forecast is structurally eligible, but predictive scoring requires an outcome observed after forecast origin; no outcome is carried by the runtime Forecast object",
        (f"origin_time={obj.origin_time.isoformat()}", f"horizon={obj.horizon}", f"target={obj.target}", f"pit={obj.point_in_time_fingerprint}"),
        "PREDICTION",
        True,
    )


__all__ = ["ExecutionOutcome", "ScientificWorkResult", "execute_scientific_work"]
