from datetime import datetime, timezone

from app.transport_security import authenticated_prediction_payload, sign_prediction_transport


def test_transport_signature_is_deterministic_for_fixed_credentials():
    payload = {"prediction_id": "p1", "probability": 0.7}
    timestamp = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc).isoformat()
    first = sign_prediction_transport(payload, secret="shared-secret", timestamp=timestamp, nonce="nonce-123456789")
    second = sign_prediction_transport(payload, secret="shared-secret", timestamp=timestamp, nonce="nonce-123456789")
    assert first == second
    assert len(first["signature"]) == 64


def test_authenticated_payload_preserves_canonical_prediction():
    payload = {"prediction_id": "p1", "probability": 0.7}
    wrapped = authenticated_prediction_payload(payload, secret="shared-secret", timestamp="2026-09-15T05:00:00+00:00", nonce="nonce-123456789")
    assert wrapped["prediction_id"] == "p1"
    assert set(wrapped["_transport"]) == {"timestamp", "nonce", "signature"}
