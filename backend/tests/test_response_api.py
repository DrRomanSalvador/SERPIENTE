from datetime import datetime, timedelta, timezone
import json

from fastapi.testclient import TestClient

from app.contracts import Alert
from app.main import app


def _alert(alert_id="A-API"):
    return Alert(alert_id=alert_id, level="HIGH", score=0.8, rationale=("test",), event_ids=("E1",), signal_ids=("S1",), forecast_ids=(), uncertainty=0.2, provenance=("source:test",))


def _payload(alert_id="A-API"):
    decision = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
    return {
        "response_id": "R-API",
        "alert_id": alert_id,
        "prediction_id": None,
        "decision_id": "D-API",
        "decision_time": decision.isoformat(),
        "action_id": "ACT-API",
        "action_time": (decision + timedelta(minutes=10)).isoformat(),
        "response_eligible": True,
        "intended_mechanism": "test response",
        "response_delay_seconds": 600.0,
        "intervention_exposure": "observed",
        "implementation_failure": None,
        "resource_capacity_constraints": None,
        "outcome_id": None,
        "outcome_time": None,
        "response_horizon": "24h",
        "causal_status": "NOT_ESTABLISHED",
        "provenance": ["test:api"],
    }


def test_response_endpoint_persists_authenticated_lineage(monkeypatch, tmp_path):
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"analyst-key": "ANALYST"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(tmp_path / "responses.sqlite"))
    with TestClient(app) as client:
        runtime = app.state.runtime
        with runtime.store.transaction():
            runtime.store.alert(_alert())
        response = client.post("/v1/responses", headers={"X-SERPIENTE-API-Key": "analyst-key"}, json=_payload())
        assert response.status_code == 200
        assert response.json()["response_id"] == "R-API"
        assert runtime.store.snapshot()["responses"] == 1


def test_response_endpoint_requires_analyst_role(monkeypatch, tmp_path):
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"ingestor-key": "INGESTOR"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(tmp_path / "responses.sqlite"))
    with TestClient(app) as client:
        response = client.post("/v1/responses", headers={"X-SERPIENTE-API-Key": "ingestor-key"}, json=_payload())
        assert response.status_code == 403
