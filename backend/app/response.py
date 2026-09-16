from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
class ResponseRecord:
    response_id: str
    alert_id: str
    prediction_id: Optional[str]
    decision_id: str
    decision_time: datetime
    action_id: str
    action_time: datetime
    response_eligible: bool
    intended_mechanism: str
    response_delay_seconds: float
    intervention_exposure: str
    implementation_failure: Optional[str]
    resource_capacity_constraints: Optional[str]
    outcome_id: Optional[str]
    outcome_time: Optional[datetime]
    response_horizon: str
    causal_status: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.response_id or not self.alert_id or not self.decision_id or not self.action_id:
            raise ValueError("response identity fields are required")
        if self.decision_time.tzinfo is None or self.action_time.tzinfo is None:
            raise ValueError("decision and action times must be timezone-aware")
        if self.action_time < self.decision_time:
            raise ValueError("action cannot precede decision")
        if self.response_delay_seconds < 0:
            raise ValueError("response delay cannot be negative")
        if not self.intended_mechanism or not self.response_horizon or not self.provenance:
            raise ValueError("response mechanism, horizon and provenance are required")
        if self.outcome_time is not None and self.outcome_time < self.action_time:
            raise ValueError("outcome cannot precede action")
        if self.outcome_id is None and self.outcome_time is not None:
            raise ValueError("outcome_time requires outcome_id")

    def to_dict(self) -> dict:
        return asdict(self)
