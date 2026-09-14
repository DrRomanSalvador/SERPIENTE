import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


def observation_payload():
    return [{"source_id":"s","dataset_id":"d","variable_id":"v","semantic_definition":"semantic","unit":"unit","geography":"Ceuta","event_time":"2026-01-01T00:00:00+00:00","publication_time":"2026-01-01T00:00:00+00:00","acquisition_time":"2026-01-01T01:00:00+00:00","source_version":"1","revision":0,"value":1.0,"provenance":["official:s"]}]


def test_observation_endpoint_requires_authentication(monkeypatch, tmp_path):
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"ingest-key":"INGESTOR"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(tmp_path / "api.sqlite"))
    with TestClient(app) as client:
        response = client.post("/v1/observations", json=observation_payload())
        assert response.status_code == 401


def test_rbac_prevents_ingestor_from_analyst_operation(monkeypatch, tmp_path):
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"ingest-key":"INGESTOR"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(tmp_path / "api.sqlite"))
    with TestClient(app) as client:
        response = client.post("/v1/process", headers={"X-SERPIENTE-API-Key":"ingest-key"}, json={"as_of":"2026-01-01T00:00:00+00:00","geography":"Ceuta","domain":"health","event_type":"event"})
        assert response.status_code == 403


def test_ingestor_can_insert_but_cannot_execute_process(monkeypatch, tmp_path):
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"ingest-key":"INGESTOR"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(tmp_path / "api.sqlite"))
    with TestClient(app) as client:
        response = client.post("/v1/observations", headers={"X-SERPIENTE-API-Key":"ingest-key"}, json=observation_payload())
        assert response.status_code == 200 and response.json()["accepted"] == 1


def test_unknown_role_is_not_accepted(monkeypatch, tmp_path):
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"bad-key":"VIEWER"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(tmp_path / "api.sqlite"))
    with TestClient(app) as client:
        response = client.post("/v1/observations", headers={"X-SERPIENTE-API-Key":"bad-key"}, json=observation_payload())
        assert response.status_code == 401
