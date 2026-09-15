from datetime import datetime, timezone

from app.runtime import SerpienteRuntime
from app.scientific_boundary import validate_ceutia_message


def test_runtime_exposes_scientific_boundary_and_receiver_rejects_ood():
    runtime = SerpienteRuntime()
    class Forecast:
        forecast_id = "p1"; origin_time = datetime(2026, 9, 15, tzinfo=timezone.utc); horizon = "1d"; target = "risk"
        probability = 0.7; lower = 0.4; upper = 0.9; aleatoric = 0.1; epistemic = 0.1; measurement = 0.0; parameter = 0.1; structural = 0.1; model_disagreement = 0.05
        provenance = ("observation:o1",); point_in_time_fingerprint = "pt"
    payload = runtime.emit_scientific_prediction(Forecast(), available_at=datetime(2026, 9, 15, 0, 1, tzinfo=timezone.utc), model_id="m1", method_id="m1", method_version="1", training_window="train", reference_class="rc", ood_state="IN_DOMAIN", causal_status="DESCRIPTIVE", calibration_status="CALIBRATED", evidence_level="observational", source_independence="INDEPENDENT", configuration_hash="cfg", code_revision="rev")
    assert validate_ceutia_message(payload).compatible
    payload["ood_state"] = "OUT_OF_DISTRIBUTION"
    assert not validate_ceutia_message(payload).compatible
