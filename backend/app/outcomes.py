from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite


@dataclass(frozen=True, slots=True)
class ForecastOutcome:
    prediction_id: str
    origin_time: datetime
    outcome_time: datetime
    target: str
    observed: float
    predicted_probability: float
    horizon: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.origin_time.tzinfo is None or self.outcome_time.tzinfo is None:
            raise ValueError("outcome timestamps must be timezone-aware")
        if self.outcome_time.astimezone(timezone.utc) < self.origin_time.astimezone(timezone.utc):
            raise ValueError("outcome cannot precede prediction origin")
        if not 0 <= self.predicted_probability <= 1 or not isfinite(self.predicted_probability):
            raise ValueError("predicted probability must be finite and in [0,1]")
        if self.observed not in (0, 1):
            raise ValueError("binary prospective outcome must be 0 or 1")
        if not self.provenance:
            raise ValueError("outcome provenance is required")

    @property
    def brier_error(self) -> float:
        return float((self.predicted_probability - self.observed) ** 2)

    @property
    def log_loss_error(self) -> float:
        p = min(max(self.predicted_probability, 1e-8), 1 - 1e-8)
        return float(-(self.observed * __import__("math").log(p) + (1 - self.observed) * __import__("math").log(1 - p)))
