"""SERPIENTE receiver/producer adapter for the canonical CeutIA contract.

The canonical contract is owned by Ceuta. This module contains only the
receiver's executable semantic checks plus a generated contract identity; it
must reject schema-valid messages whose scientific state is unusable.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

CANONICAL_CONTRACT_ID = "ceutia-serpiente-scientific-prediction"
CANONICAL_CONTRACT_VERSION = "1.1"
CANONICAL_CONTRACT_HASH = "672dfa6b60d2e8c0854a024e83acf6b23eed44f2cd3293708aee533d7a9dc1f0"


@dataclass(frozen=True, slots=True)
class ScientificCompatibilityResult:
    compatible: bool
    reasons: tuple[str, ...]
    contract_version: str


def validate_ceutia_message(payload: dict[str, Any]) -> ScientificCompatibilityResult:
    reasons: list[str] = []
    if payload.get("contract_id") != CANONICAL_CONTRACT_ID:
        reasons.append("contract_identity_mismatch")
    if payload.get("contract_hash") != CANONICAL_CONTRACT_HASH:
        reasons.append("contract_hash_mismatch")
    required = ("prediction_id", "origin_time", "available_at", "horizon", "target", "probability", "lower", "upper", "uncertainty", "model_id", "method_id", "method_version", "training_window", "reference_class", "ood_state", "causal_status", "calibration_status", "evidence_level", "source_independence", "provenance", "configuration_hash", "code_revision", "point_in_time_fingerprint", "integrity_hash")
    missing = [name for name in required if name not in payload]
    if missing:
        reasons.append("scientific_contract_missing_fields:" + ",".join(missing))
        return ScientificCompatibilityResult(False, tuple(reasons), str(payload.get("schema_version", "unknown")))
    if payload["ood_state"] == "OUT_OF_DISTRIBUTION":
        reasons.append("out_of_distribution")
    if payload["ood_state"] == "UNKNOWN":
        reasons.append("ood_state_unknown")
    if payload["causal_status"] == "ABSTAIN":
        reasons.append("causal_identification_abstained")
    if payload["calibration_status"] != "CALIBRATED":
        reasons.append("forecast_not_calibrated")
    if payload["source_independence"] == "UNKNOWN":
        reasons.append("source_independence_unknown")
    if not payload["provenance"] or not payload["point_in_time_fingerprint"]:
        reasons.append("provenance_incomplete")
    try:
        origin = datetime.fromisoformat(payload["origin_time"])
        available = datetime.fromisoformat(payload["available_at"])
        if origin.tzinfo is None or available.tzinfo is None or available < origin:
            reasons.append("temporal_availability_invalid")
        if not all(math.isfinite(float(v)) for v in (payload["probability"], payload["lower"], payload["upper"])):
            reasons.append("non_finite_forecast")
        if not 0 <= float(payload["probability"]) <= 1 or float(payload["lower"]) > float(payload["upper"]):
            reasons.append("forecast_domain_invalid")
    except (TypeError, ValueError):
        reasons.append("temporal_or_numeric_semantics_invalid")
    canonical = dict(payload)
    canonical.pop("integrity_hash", None)
    expected = sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    if expected != payload["integrity_hash"]:
        reasons.append("integrity_hash_mismatch")
    # UNKNOWN OOD/dependence and non-calibration are valid machine states, but
    # they are scientifically incompatible with automatic downstream release.
    return ScientificCompatibilityResult(not reasons, tuple(reasons), str(payload["schema_version"]))


def make_scientific_prediction_payload(*, prediction_id: str, origin_time: datetime, available_at: datetime, horizon: str, target: str, probability: float, lower: float, upper: float, uncertainty: dict[str, float], model_disagreement: float, model_id: str, method_id: str, method_version: str, training_window: str, reference_class: str, ood_state: str, causal_status: str, calibration_status: str, evidence_level: str, source_independence: str, provenance: tuple[str, ...], configuration_hash: str, code_revision: str, point_in_time_fingerprint: str) -> dict[str, Any]:
    if origin_time.tzinfo is None or available_at.tzinfo is None:
        raise ValueError("scientific contract timestamps must be timezone-aware")
    payload: dict[str, Any] = {
        "contract_id": CANONICAL_CONTRACT_ID, "contract_hash": CANONICAL_CONTRACT_HASH,
        "producer_repository": "DrRomanSalvador/SERPIENTE", "producer_component": "serpiente-runtime",
        "schema_version": CANONICAL_CONTRACT_VERSION, "prediction_id": prediction_id,
        "origin_time": origin_time.astimezone(timezone.utc).isoformat(), "available_at": available_at.astimezone(timezone.utc).isoformat(),
        "horizon": horizon, "target": target, "probability": probability, "lower": lower, "upper": upper,
        "uncertainty": uncertainty, "model_disagreement": model_disagreement, "model_id": model_id,
        "method_id": method_id, "method_version": method_version, "training_window": training_window,
        "reference_class": reference_class, "ood_state": ood_state, "causal_status": causal_status,
        "calibration_status": calibration_status, "evidence_level": evidence_level, "source_independence": source_independence,
        "provenance": provenance, "configuration_hash": configuration_hash, "code_revision": code_revision,
        "point_in_time_fingerprint": point_in_time_fingerprint,
    }
    payload["integrity_hash"] = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    return payload


__all__ = ["CANONICAL_CONTRACT_HASH", "CANONICAL_CONTRACT_ID", "CANONICAL_CONTRACT_VERSION", "ScientificCompatibilityResult", "make_scientific_prediction_payload", "validate_ceutia_message"]
