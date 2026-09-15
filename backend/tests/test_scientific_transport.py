from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.scientific_transport import build_authenticated_prediction, sign_prediction


def _payload() -> dict[str, object]:
    return {"contract_id": "ceutia-serpiente-scientific-prediction", "prediction_id": "p-1", "probability": 0.7}


def test_authenticated_prediction_contains_verifiable_transport_fields() -> None:
    payload = _payload()
    timestamp = datetime(2026, 9, 15, 7, 0, tzinfo=timezone.utc).isoformat()
    wrapped = build_authenticated_prediction(payload, secret="shared-secret", timestamp=timestamp, nonce="0123456789abcdef")
    transport = wrapped["_transport"]
    assert transport == {
        "timestamp": timestamp,
        "nonce": "0123456789abcdef",
        "signature": sign_prediction(payload, secret="shared-secret", timestamp=timestamp, nonce="0123456789abcdef"),
    }
    assert {key for key in wrapped if key != "_transport"} == set(payload)


def test_authenticated_prediction_requires_secret() -> None:
    with pytest.raises(ValueError, match="transport secret"):
        build_authenticated_prediction(_payload(), secret="")


def test_authenticated_prediction_rejects_non_string_nonce_at_boundary() -> None:
    with pytest.raises(TypeError):
        build_authenticated_prediction(_payload(), secret="shared-secret", nonce=object())  # type: ignore[arg-type]
