from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from dataclasses import dataclass
from typing import Any

from .contracts import Forecast


CONTRACT_ID = "ceutia-serpiente-scientific-prediction"
CONTRACT_VERSION = "1.1"
CONTRACT_FIELDS = (
    "producer_repository", "producer_component", "schema_version", "prediction_id",
    "origin_time", "available_at", "horizon", "target", "probability", "lower", "upper",
    "uncertainty", "model_disagreement", "model_id", "method_id", "method_version",
    "training_window", "reference_class", "ood_state", "causal_status", "calibration_status",
    "evidence_level", "source_independence", "provenance", "configuration_hash", "code_revision",
    "point_in_time_fingerprint", "integrity_hash",
)


def canonical_contract_hash() -> str:
    payload = {"contract_id": CONTRACT_ID, "version": CONTRACT_VERSION, "fields": CONTRACT_FIELDS}
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


CANONICAL_CONTRACT_HASH = canonical_contract_hash()


@dataclass(frozen=True, slots=True)
class ScientificPredictionMetadata:
    model_id: str
    method_id: str
    method_version: str
    training_window: str
    reference_class: str
    ood_state: str
    causal_status: str
    calibration_status: str
    evidence_level: str
    source_independence: str
    configuration_hash: str
    code_revision: str

    def __post_init__(self) -> None:
        required = (
            self.model_id, self.method_id, self.method_version, self.training_window,
            self.reference_class, self.configuration_hash, self.code_revision,
        )
        if not all(required):
            raise ValueError("scientific prediction metadata is incomplete")
        if self.ood_state not in {"IN_DOMAIN", "NEAR_BOUNDARY", "OUT_OF_DISTRIBUTION", "UNKNOWN"}:
            raise ValueError("invalid OOD state")
        if self.causal_status not in {"DESCRIPTIVE", "CONDITIONAL", "IDENTIFIED", "ABSTAIN"}:
            raise ValueError("invalid causal status")
        if self.calibration_status not in {"CALIBRATED", "UNCALIBRATED", "UNKNOWN"}:
            raise ValueError("invalid calibration status")
        if self.source_independence not in {"INDEPENDENT", "DEPENDENT", "PARTIALLY_DEPENDENT", "UNKNOWN"}:
            raise ValueError("invalid source independence")


def forecast_to_scientific_prediction(
    forecast: Forecast,
    *,
    available_at: datetime,
    metadata: ScientificPredictionMetadata,
    producer_component: str = "SERPIENTE.LongitudinalForecaster",
) -> dict[str, Any]:
    if available_at.tzinfo is None:
        raise ValueError("available_at must be timezone-aware")
    available_at = available_at.astimezone(timezone.utc)
    if available_at < forecast.origin_time:
        raise ValueError("available_at cannot precede forecast origin")
    if not producer_component:
        raise ValueError("producer_component is required")
    payload: dict[str, Any] = {
        "contract_id": CONTRACT_ID,
        "contract_hash": CANONICAL_CONTRACT_HASH,
        "producer_repository": "DrRomanSalvador/SERPIENTE",
        "producer_component": producer_component,
        "schema_version": CONTRACT_VERSION,
        "prediction_id": str(forecast.forecast_id),
        "origin_time": forecast.origin_time.astimezone(timezone.utc).isoformat(),
        "available_at": available_at.isoformat(),
        "horizon": forecast.horizon,
        "target": forecast.target,
        "probability": forecast.probability,
        "lower": forecast.lower,
        "upper": forecast.upper,
        "uncertainty": {
            "aleatoric": forecast.aleatoric,
            "epistemic": forecast.epistemic,
            "measurement": forecast.measurement,
            "parameter": forecast.parameter,
            "structural": forecast.structural,
        },
        "model_disagreement": forecast.model_disagreement,
        "model_id": metadata.model_id,
        "method_id": metadata.method_id,
        "method_version": metadata.method_version,
        "training_window": metadata.training_window,
        "reference_class": metadata.reference_class,
        "ood_state": metadata.ood_state,
        "causal_status": metadata.causal_status,
        "calibration_status": metadata.calibration_status,
        "evidence_level": metadata.evidence_level,
        "source_independence": metadata.source_independence,
        "provenance": tuple(forecast.provenance),
        "configuration_hash": metadata.configuration_hash,
        "code_revision": metadata.code_revision,
        "point_in_time_fingerprint": forecast.point_in_time_fingerprint,
    }
    payload["integrity_hash"] = sha256(
        json.dumps({key: value for key, value in payload.items() if key not in {"integrity_hash"}}, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()
    return payload


__all__ = [
    "CANONICAL_CONTRACT_HASH",
    "CONTRACT_ID",
    "CONTRACT_VERSION",
    "ScientificPredictionMetadata",
    "forecast_to_scientific_prediction",
]
