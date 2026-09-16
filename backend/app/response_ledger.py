"""Canonical warning-to-response lifecycle contract for CeutIA/SERPIENTE.

This module deliberately separates predictive validity, response execution,
response effectiveness and operational utility. A temporal link between a
warning, an action and an outcome is never treated as a causal effect.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from math import isfinite
from typing import Mapping


class ResponseStatus(StrEnum):
    NO_RESPONSE = "NO_RESPONSE"
    PROPOSED = "PROPOSED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    OUTSIDE_WINDOW = "OUTSIDE_WINDOW"


class CausalStatus(StrEnum):
    NOT_ASSESSED = "NOT_ASSESSED"
    DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"
    IDENTIFICATION_REQUIRED = "IDENTIFICATION_REQUIRED"
    IDENTIFIED = "IDENTIFIED"


@dataclass(frozen=True, slots=True)
class ResponseLedgerRecord:
    response_id: str
    alert_id: str
    prediction_id: str | None
    decision_id: str | None
    decision_time: datetime | None
    action_id: str | None
    action_time: datetime | None
    response_status: ResponseStatus
    response_eligible: bool
    eligible_from: datetime
    eligible_until: datetime
    intended_mechanism: str
    response_delay_seconds: float | None
    intervention_exposure: str | None
    implementation_failure: str | None
    resource_capacity_constraints: str | None
    outcome_id: str | None
    outcome_time: datetime | None
    response_horizon: str
    outcome_ascertainment_ref: str | None
    counterfactual_ref: str | None
    causal_status: CausalStatus
    provenance: tuple[str, ...]
    actor_context: str | None = None

    def __post_init__(self) -> None:
        if not self.response_id or not self.alert_id:
            raise ValueError("response identity requires response_id and alert_id")
        for name in ("eligible_from", "eligible_until"):
            value = getattr(self, name)
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        start = self.eligible_from.astimezone(timezone.utc)
        end = self.eligible_until.astimezone(timezone.utc)
        if end <= start:
            raise ValueError("eligible_until must be after eligible_from")
        object.__setattr__(self, "eligible_from", start)
        object.__setattr__(self, "eligible_until", end)

        for name in ("decision_time", "action_time", "outcome_time"):
            value = getattr(self, name)
            if value is not None:
                if value.tzinfo is None or value.utcoffset() is None:
                    raise ValueError(f"{name} must be timezone-aware")
                object.__setattr__(self, name, value.astimezone(timezone.utc))

        if not self.intended_mechanism or not self.response_horizon or not self.provenance:
            raise ValueError("mechanism, response horizon and provenance are required")
        if self.response_delay_seconds is not None:
            if not isfinite(self.response_delay_seconds) or self.response_delay_seconds < 0:
                raise ValueError("response_delay_seconds must be finite and non-negative")

        executed = self.response_status is ResponseStatus.EXECUTED
        if executed and (not self.decision_id or self.decision_time is None or not self.action_id or self.action_time is None):
            raise ValueError("EXECUTED response requires decision and action identity/times")
        if self.action_time is not None and self.decision_time is None:
            raise ValueError("action_time requires decision_time")
        if self.action_id is not None and self.decision_id is None:
            raise ValueError("action_id requires decision_id")
        if self.action_time is not None and self.decision_time is not None and self.action_time < self.decision_time:
            raise ValueError("action cannot precede decision")
        if self.response_delay_seconds is not None and self.action_time is not None and self.decision_time is not None:
            actual_delay = (self.action_time - self.decision_time).total_seconds()
            if abs(actual_delay - self.response_delay_seconds) > 1e-6:
                raise ValueError("response_delay_seconds does not match decision/action timestamps")

        if self.response_status is ResponseStatus.NO_RESPONSE:
            if self.action_id is not None or self.action_time is not None:
                raise ValueError("NO_RESPONSE cannot contain an executed action")
            if not self.implementation_failure and self.response_eligible:
                raise ValueError("eligible NO_RESPONSE requires a non-execution reason")

        if self.outcome_time is not None and self.outcome_id is None:
            raise ValueError("outcome_time requires outcome_id")
        if self.outcome_id is not None and self.action_id is None:
            raise ValueError("outcome cannot be attached without intervention exposure")
        if self.outcome_time is not None and self.action_time is not None and self.outcome_time < self.action_time:
            raise ValueError("outcome cannot precede action")

        if self.causal_status is CausalStatus.IDENTIFIED and not self.counterfactual_ref:
            raise ValueError("IDENTIFIED causal status requires an explicit counterfactual reference")
        if self.causal_status is CausalStatus.IDENTIFIED and not self.outcome_ascertainment_ref:
            raise ValueError("IDENTIFIED causal status requires outcome ascertainment provenance")

        if self.action_time is not None and self.response_eligible:
            if not start <= self.action_time <= end:
                raise ValueError("executed eligible response must occur inside the declared response window")

    def is_currently_eligible(self, at: datetime) -> bool:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("eligibility time must be timezone-aware")
        moment = at.astimezone(timezone.utc)
        return self.response_eligible and self.eligible_from <= moment <= self.eligible_until

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        for key in ("decision_time", "action_time", "eligible_from", "eligible_until", "outcome_time"):
            if payload[key] is not None:
                payload[key] = payload[key].isoformat()
        payload["response_status"] = self.response_status.value
        payload["causal_status"] = self.causal_status.value
        return payload


def _timestamp(value: object, field: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 string or null")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return parsed


def validate_response_payload(payload: Mapping[str, object]) -> ResponseLedgerRecord:
    """Deserialize and validate a transport-shaped response without filling missing stages."""
    required = {
        "response_id", "alert_id", "response_status", "response_eligible",
        "eligible_from", "eligible_until", "intended_mechanism", "response_horizon",
        "causal_status", "provenance",
    }
    missing = sorted(key for key in required if key not in payload)
    if missing:
        raise ValueError(f"response payload missing required fields: {', '.join(missing)}")
    provenance = payload["provenance"]
    if not isinstance(provenance, (list, tuple)) or not provenance or any(not isinstance(x, str) or not x for x in provenance):
        raise ValueError("provenance must be a non-empty sequence of non-empty strings")
    try:
        status = ResponseStatus(str(payload["response_status"]))
        causal_status = CausalStatus(str(payload["causal_status"]))
    except ValueError as exc:
        raise ValueError("invalid response_status or causal_status") from exc
    return ResponseLedgerRecord(
        response_id=str(payload["response_id"]),
        alert_id=str(payload["alert_id"]),
        prediction_id=None if payload.get("prediction_id") is None else str(payload["prediction_id"]),
        decision_id=None if payload.get("decision_id") is None else str(payload["decision_id"]),
        decision_time=_timestamp(payload.get("decision_time"), "decision_time"),
        action_id=None if payload.get("action_id") is None else str(payload["action_id"]),
        action_time=_timestamp(payload.get("action_time"), "action_time"),
        response_status=status,
        response_eligible=bool(payload["response_eligible"]),
        eligible_from=_timestamp(payload["eligible_from"], "eligible_from") or datetime.min.replace(tzinfo=timezone.utc),
        eligible_until=_timestamp(payload["eligible_until"], "eligible_until") or datetime.min.replace(tzinfo=timezone.utc),
        intended_mechanism=str(payload["intended_mechanism"]),
        response_delay_seconds=None if payload.get("response_delay_seconds") is None else float(payload["response_delay_seconds"]),
        intervention_exposure=None if payload.get("intervention_exposure") is None else str(payload["intervention_exposure"]),
        implementation_failure=None if payload.get("implementation_failure") is None else str(payload["implementation_failure"]),
        resource_capacity_constraints=None if payload.get("resource_capacity_constraints") is None else str(payload["resource_capacity_constraints"]),
        outcome_id=None if payload.get("outcome_id") is None else str(payload["outcome_id"]),
        outcome_time=_timestamp(payload.get("outcome_time"), "outcome_time"),
        response_horizon=str(payload["response_horizon"]),
        outcome_ascertainment_ref=None if payload.get("outcome_ascertainment_ref") is None else str(payload["outcome_ascertainment_ref"]),
        counterfactual_ref=None if payload.get("counterfactual_ref") is None else str(payload["counterfactual_ref"]),
        causal_status=causal_status,
        provenance=tuple(provenance),
        actor_context=None if payload.get("actor_context") is None else str(payload["actor_context"]),
    )


__all__ = ["CausalStatus", "ResponseLedgerRecord", "ResponseStatus", "validate_response_payload"]
