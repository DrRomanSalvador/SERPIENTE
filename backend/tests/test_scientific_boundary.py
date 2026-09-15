from datetime import datetime, timezone

from app.scientific_boundary import make_scientific_prediction_payload, validate_ceutia_message


def _payload(**overrides):
    payload = make_scientific_prediction_payload(
        prediction_id="p1", origin_time=datetime(2026, 9, 15, tzinfo=timezone.utc),
        available_at=datetime(2026, 9, 15, 0, 1, tzinfo=timezone.utc), horizon="1d", target="risk",
        probability=0.7, lower=0.4, upper=0.9, uncertainty={"epistemic": 0.1}, model_disagreement=0.05,
        model_id="longitudinal_ensemble", method_id="longitudinal-forecast", method_version="1",
        training_window="2026-train", reference_class="risk-class-v1", ood_state="IN_DOMAIN",
        causal_status="DESCRIPTIVE", calibration_status="CALIBRATED", evidence_level="observational",
        source_independence="INDEPENDENT", provenance=("observation:o1",), configuration_hash="cfg", code_revision="rev",
        point_in_time_fingerprint="pt-fp",
    )
    payload.update(overrides)
    return payload


def test_canonical_payload_is_accepted():
    result = validate_ceutia_message(_payload())
    assert result.compatible
    assert result.reasons == ()


def test_schema_valid_but_ood_payload_is_rejected():
    result = validate_ceutia_message(_payload(ood_state="OUT_OF_DISTRIBUTION"))
    assert not result.compatible
    assert "out_of_distribution" in result.reasons


def test_temporal_violation_is_rejected():
    result = validate_ceutia_message(_payload(available_at="2026-09-14T00:00:00+00:00"))
    assert not result.compatible
    assert "temporal_availability_invalid" in result.reasons


def test_tampered_integrity_is_rejected():
    result = validate_ceutia_message(_payload(probability=0.71))
    assert not result.compatible
    assert "integrity_hash_mismatch" in result.reasons
