from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any

from .contracts import Alert, Forecast


@dataclass(frozen=True, slots=True)
class CeutIAPredictionEnvelope:
    schema_version: str
    prediction_id: str
    origin_time: datetime
    horizon: str
    target: str
    probability: float
    lower: float
    upper: float
    uncertainty: dict[str, float]
    model_disagreement: float
    regime: str
    provenance: tuple[str, ...]
    point_in_time_fingerprint: str
    alert_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["origin_time"] = self.origin_time.astimezone(timezone.utc).isoformat()
        return data

    def canonical_hash(self) -> str:
        return sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()


def prediction_to_ceutia(forecast: Forecast, alerts: tuple[Alert, ...] = ()) -> CeutIAPredictionEnvelope:
    if forecast.origin_time.tzinfo is None:
        raise ValueError("forecast origin must be timezone-aware")
    if not forecast.provenance or not forecast.point_in_time_fingerprint:
        raise ValueError("forecast provenance and point-in-time fingerprint are mandatory")
    return CeutIAPredictionEnvelope(
        schema_version="1.0",
        prediction_id=str(forecast.forecast_id),
        origin_time=forecast.origin_time,
        horizon=forecast.horizon,
        target=forecast.target,
        probability=forecast.probability,
        lower=forecast.lower,
        upper=forecast.upper,
        uncertainty={"aleatoric": forecast.aleatoric, "epistemic": forecast.epistemic, "measurement": forecast.measurement, "parameter": forecast.parameter, "structural": forecast.structural},
        model_disagreement=forecast.model_disagreement,
        regime=forecast.regime,
        provenance=forecast.provenance,
        point_in_time_fingerprint=forecast.point_in_time_fingerprint,
        alert_ids=tuple(str(a.alert_id) for a in alerts),
    )
