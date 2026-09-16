from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log


@dataclass(frozen=True, slots=True)
class ForecastOutcome:
    prediction_id: str
    origin_time: datetime
    outcome_time: datetime
    target: str
    observed: int
    predicted_probability: float
    horizon: str
    provenance: tuple[str, ...]
    available_at: datetime | None = None
    vintage_id: str | None = None
    definition_version: str = "v1"

    def __post_init__(self) -> None:
        if self.origin_time.tzinfo is None or self.outcome_time.tzinfo is None:
            raise ValueError("outcome timestamps must be timezone-aware")
        origin = self.origin_time.astimezone(timezone.utc)
        outcome = self.outcome_time.astimezone(timezone.utc)
        if outcome < origin:
            raise ValueError("outcome cannot precede prediction origin")
        if self.available_at is not None:
            if self.available_at.tzinfo is None:
                raise ValueError("available_at must be timezone-aware")
            available = self.available_at.astimezone(timezone.utc)
            if available < outcome:
                raise ValueError("available_at cannot precede outcome_time")
            object.__setattr__(self, "available_at", available)
        if not 0 <= self.predicted_probability <= 1 or not isfinite(self.predicted_probability):
            raise ValueError("predicted probability must be finite and in [0,1]")
        if self.observed not in (0, 1):
            raise ValueError("binary prospective outcome must be 0 or 1")
        if not self.prediction_id or not self.target or not self.horizon or not self.provenance:
            raise ValueError("complete prospective outcome identity and provenance are required")
        if self.vintage_id is not None and not self.vintage_id.strip():
            raise ValueError("vintage_id cannot be blank")
        if not self.definition_version.strip():
            raise ValueError("definition_version cannot be blank")
        object.__setattr__(self, "origin_time", origin)
        object.__setattr__(self, "outcome_time", outcome)

    def eligible_at(self, cutoff: datetime) -> bool:
        if cutoff.tzinfo is None:
            raise ValueError("cutoff must be timezone-aware")
        return self.available_at is not None and self.available_at <= cutoff.astimezone(timezone.utc)

    @property
    def brier_error(self) -> float:
        return float((self.predicted_probability - self.observed) ** 2)

    @property
    def log_loss_error(self) -> float:
        p = min(max(self.predicted_probability, 1e-8), 1 - 1e-8)
        return float(-(self.observed * log(p) + (1 - self.observed) * log(1 - p)))
