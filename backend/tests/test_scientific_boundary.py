from datetime import datetime, timezone

import pytest

from app.contracts import Forecast
from app.scientific_boundary import (
    CANONICAL_CONTRACT_HASH,
    ScientificPredictionMetadata,
    forecast_to_scientific_prediction,
)


def _forecast() -> Forecast:
    now = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)
    return Forecast(
        "prediction-1", now, "24h", "risk", 0.7, 0.5, 0.9,
        0.1, 0.2, 0.0, 0.1, 0.1, 0.1, "STABLE",
        ("official:source",), "p" * 64,
    )


def _metadata() -> ScientificPredictionMetadata:
    return ScientificPredictionMetadata(
        model_id="longitudinal_ensemble",
        method_id="longitudinal_forecaster",
        method_version="1",
        training_window="2026-01-01/2026-09-01",
        reference_class="Ceuta",
        ood_state="IN_DOMAIN",
        causal_status="ABSTAIN",
        calibration_status="CALIBRATED",
        evidence_level="PREDICTIVE",
        source_independence="INDEPENDENT",
        configuration_hash="c" * 64,
        code_revision="r" * 40,
    )


def test_forecast_producer_emits_canonical_contract():
    payload = forecast_to_scientific_prediction(
        _forecast(), available_at=datetime(2026, 9, 15, 5, 1, tzinfo=timezone.utc), metadata=_metadata()
    )
    assert payload["contract_id"] == "ceutia-serpiente-scientific-prediction"
    assert payload["contract_hash"] == CANONICAL_CONTRACT_HASH
    assert payload["schema_version"] == "1.1"
    assert payload["prediction_id"] == "prediction-1"
    assert len(payload["integrity_hash"]) == 64


def test_forecast_producer_rejects_pre_origin_availability():
    with pytest.raises(ValueError, match="cannot precede"):
        forecast_to_scientific_prediction(
            _forecast(), available_at=datetime(2026, 9, 15, 4, 59, tzinfo=timezone.utc), metadata=_metadata()
        )
