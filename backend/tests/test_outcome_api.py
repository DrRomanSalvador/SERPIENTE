from datetime import datetime, timedelta, timezone
import json

from fastapi.testclient import TestClient

from app.contracts import Forecast
from app.main import app


def test_outcome_endpoint_links_to_persisted_forecast(monkeypatch, tmp_path):
    db = tmp_path / "outcomes.sqlite"
    monkeypatch.setenv("SERPIENTE_API_KEYS_JSON", json.dumps({"analyst-key":"ANALYST"}))
    monkeypatch.setenv("SERPIENTE_RUNTIME_DB", str(db))
    with TestClient(app) as client:
        runtime = app.state.runtime
        origin = datetime(2026,1,1,tzinfo=timezone.utc)
        forecast = Forecast("p1", origin, "24h", "risk", 0.8, 0.4, 1.0, 0.2, 0.1, 0.0, 0.1, 0.2, 0.0, "STABLE", ("official",), "a"*64)
        with runtime.store.transaction():
            runtime.store.forecast(forecast)
        response = client.post("/v1/outcomes", headers={"X-SERPIENTE-API-Key":"analyst-key"}, json={"prediction_id":"p1","outcome_time":"2026-01-02T00:00:00+00:00","target":"risk","observed":1,"provenance":["official:outcome"]})
        assert response.status_code == 200
        assert response.json()["brier_error"] == 0.04
        assert runtime.store.snapshot()["outcomes"] == 1
