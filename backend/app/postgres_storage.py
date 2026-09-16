from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import asdict
from typing import Any, Iterator

import psycopg

from .contracts import Alert, Event, Forecast, Observation, Signal
from .outcomes import ForecastOutcome
from .response import ResponseRecord
from .scientific_discovery_engine import ScientificClaim, ScientificWork
from .scientific_work_execution import ScientificWorkResult


class PostgresRuntimeStore:
    def __init__(self, dsn: str) -> None:
        if not dsn.strip():
            raise ValueError("PostgreSQL DSN is required")
        self.db = psycopg.connect(dsn, autocommit=True)

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self.db.transaction():
            yield

    def close(self) -> None:
        self.db.close()

    @staticmethod
    def _json(payload: dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, default=str)

    def observation(self, item: Observation) -> None:
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO serpiente_observations(id,event_time,publication_time,acquisition_time,payload) VALUES (%s,%s,%s,%s,%s::jsonb)", (str(item.observation_id), item.event_time, item.publication_time, item.acquisition_time, self._json(item.to_dict())))

    def event(self, item: Event) -> None:
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO serpiente_events(id,event_time,payload) VALUES (%s,%s,%s::jsonb)", (str(item.event_id), item.event_time, self._json(asdict(item))))

    def signal(self, item: Signal) -> None:
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO serpiente_signals(id,payload) VALUES (%s,%s::jsonb)", (str(item.signal_id), self._json(asdict(item))))

    def forecast(self, item: Forecast) -> None:
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO serpiente_forecasts(id,origin_time,payload) VALUES (%s,%s,%s::jsonb)", (str(item.forecast_id), item.origin_time, self._json(asdict(item))))

    def scientific_work(self, item: ScientificWork) -> None:
        encoded = self._json(asdict(item))
        fingerprint = json.dumps(item.fingerprint, sort_keys=True, default=str)
        with self.db.cursor() as cur:
            cur.execute("SELECT fingerprint,payload FROM serpiente_scientific_work WHERE id=%s FOR UPDATE", (item.work_id,))
            existing = cur.fetchone()
            if existing is not None:
                if existing[0] != json.loads(fingerprint) or existing[1] != json.loads(encoded):
                    raise RuntimeError("scientific work identity collision")
                return
            cur.execute("INSERT INTO serpiente_scientific_work(id,fingerprint,payload) VALUES (%s,%s::jsonb,%s::jsonb)", (item.work_id, fingerprint, encoded))

    def scientific_result(self, item: ScientificWorkResult) -> None:
        key = f"{item.work_id}:{item.runtime_id}"
        encoded = self._json(asdict(item))
        with self.db.cursor() as cur:
            cur.execute("SELECT payload FROM serpiente_scientific_results WHERE id=%s FOR UPDATE", (key,))
            existing = cur.fetchone()
            if existing is not None:
                if existing[0] != json.loads(encoded):
                    raise RuntimeError("scientific result identity collision")
                return
            cur.execute("INSERT INTO serpiente_scientific_results(id,work_id,runtime_id,payload) VALUES (%s,%s,%s,%s::jsonb)", (key, item.work_id, item.runtime_id, encoded))

    def scientific_claim(self, item: ScientificClaim) -> None:
        encoded = self._json(asdict(item))
        with self.db.cursor() as cur:
            cur.execute("SELECT payload FROM serpiente_scientific_claims WHERE id=%s FOR UPDATE", (item.claim_id,))
            existing = cur.fetchone()
            if existing is not None and existing[0] != json.loads(encoded):
                raise RuntimeError("scientific claim identity collision")
            if existing is None:
                cur.execute("INSERT INTO serpiente_scientific_claims(id,payload) VALUES (%s,%s::jsonb)", (item.claim_id, encoded))
            else:
                cur.execute("UPDATE serpiente_scientific_claims SET payload=%s::jsonb WHERE id=%s", (encoded, item.claim_id))

    def forecast_payload(self, prediction_id: str) -> dict[str, Any] | None:
        with self.db.cursor() as cur:
            cur.execute("SELECT payload FROM serpiente_forecasts WHERE id = %s", (prediction_id,))
            row = cur.fetchone()
        return row[0] if row else None

    def alert(self, item: Alert) -> None:
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO serpiente_alerts(id,payload) VALUES (%s,%s::jsonb)", (str(item.alert_id), self._json(asdict(item))))

    def outcome(self, item: ForecastOutcome) -> None:
        encoded = self._json(asdict(item))
        with self.db.transaction():
            with self.db.cursor() as cur:
                cur.execute("SELECT 1 FROM serpiente_forecasts WHERE id = %s", (item.prediction_id,))
                if cur.fetchone() is None:
                    raise ValueError("forecast must exist before recording its outcome")
                cur.execute("INSERT INTO serpiente_outcomes(prediction_id,outcome_time,payload) VALUES (%s,%s,%s::jsonb) ON CONFLICT (prediction_id) DO NOTHING RETURNING prediction_id", (item.prediction_id, item.outcome_time, encoded))
                inserted = cur.fetchone()
                if inserted is not None:
                    return
                cur.execute("SELECT outcome_time,payload FROM serpiente_outcomes WHERE prediction_id=%s FOR UPDATE", (item.prediction_id,))
                existing = cur.fetchone()
                if existing is None:
                    raise RuntimeError("forecast outcome disappeared during idempotent delivery")
                if existing[0] != item.outcome_time or existing[1] != json.loads(encoded):
                    raise RuntimeError("forecast outcome identity collision: existing outcome differs")

    def response(self, item: ResponseRecord) -> None:
        encoded = self._json(item.to_dict())
        with self.db.transaction():
            with self.db.cursor() as cur:
                cur.execute("SELECT 1 FROM serpiente_alerts WHERE id=%s", (item.alert_id,))
                if cur.fetchone() is None:
                    raise ValueError("alert must exist before recording response")
                if item.prediction_id is not None:
                    cur.execute("SELECT 1 FROM serpiente_forecasts WHERE id=%s", (item.prediction_id,))
                    if cur.fetchone() is None:
                        raise ValueError("prediction_id must reference a persisted forecast")
                cur.execute("SELECT payload FROM serpiente_responses WHERE id=%s FOR UPDATE", (item.response_id,))
                existing = cur.fetchone()
                if existing is not None:
                    if existing[0] != json.loads(encoded):
                        raise RuntimeError("response identity collision: existing response differs")
                    return
                cur.execute("INSERT INTO serpiente_responses(id,alert_id,decision_time,action_time,outcome_time,payload) VALUES (%s,%s,%s,%s,%s,%s::jsonb)", (item.response_id, item.alert_id, item.decision_time, item.action_time, item.outcome_time, encoded))

    def snapshot(self) -> dict[str, int]:
        queries = (("observations", "SELECT COUNT(*) FROM serpiente_observations"), ("events", "SELECT COUNT(*) FROM serpiente_events"), ("signals", "SELECT COUNT(*) FROM serpiente_signals"), ("forecasts", "SELECT COUNT(*) FROM serpiente_forecasts"), ("alerts", "SELECT COUNT(*) FROM serpiente_alerts"), ("outcomes", "SELECT COUNT(*) FROM serpiente_outcomes"), ("responses", "SELECT COUNT(*) FROM serpiente_responses"), ("scientific_work", "SELECT COUNT(*) FROM serpiente_scientific_work"), ("scientific_results", "SELECT COUNT(*) FROM serpiente_scientific_results"), ("scientific_claims", "SELECT COUNT(*) FROM serpiente_scientific_claims"))
        with self.db.cursor() as cur:
            result = {}
            for key, query in queries:
                cur.execute(query)
                result[key] = cur.fetchone()[0]
        return result
