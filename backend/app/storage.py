from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterator

from .contracts import Alert, Event, Forecast, Observation, Signal
from .outcomes import ForecastOutcome
from .response import ResponseRecord


class RuntimeStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS observations (id TEXT PRIMARY KEY, event_time TEXT NOT NULL, publication_time TEXT NOT NULL, acquisition_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, event_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS signals (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS forecasts (id TEXT PRIMARY KEY, origin_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS outcomes (id INTEGER PRIMARY KEY AUTOINCREMENT, prediction_id TEXT NOT NULL, outcome_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS responses (id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, decision_time TEXT NOT NULL, action_time TEXT NOT NULL, outcome_time TEXT, payload TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_observations_event_time ON observations(event_time);
        CREATE INDEX IF NOT EXISTS idx_forecasts_origin_time ON forecasts(origin_time);
        CREATE INDEX IF NOT EXISTS idx_outcomes_prediction_id ON outcomes(prediction_id);
        CREATE INDEX IF NOT EXISTS idx_responses_alert_id ON responses(alert_id);
        """)
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(observations)")}
        if "publication_time" not in columns:
            self.db.execute("ALTER TABLE observations ADD COLUMN publication_time TEXT")
            self.db.execute("UPDATE observations SET publication_time = event_time WHERE publication_time IS NULL")
        if "acquisition_time" not in columns:
            self.db.execute("ALTER TABLE observations ADD COLUMN acquisition_time TEXT")
            self.db.execute("UPDATE observations SET acquisition_time = event_time WHERE acquisition_time IS NULL")

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._lock:
            if self.db.in_transaction:
                yield
                return
            self.db.execute("BEGIN IMMEDIATE")
            try: yield
            except Exception: self.db.rollback(); raise
            else: self.db.commit()

    def close(self) -> None:
        with self._lock: self.db.close()

    def _insert(self, table: str, key: str, timestamp: str, payload: dict[str, Any]) -> None:
        with self._lock:
            encoded=json.dumps(payload,sort_keys=True,default=str)
            if table=="observations": self.db.execute("INSERT INTO observations(id,event_time,publication_time,acquisition_time,payload) VALUES(?,?,?,?,?)",(key,payload["event_time"],payload["publication_time"],payload["acquisition_time"],encoded))
            elif table=="events": self.db.execute("INSERT INTO events(id,event_time,payload) VALUES(?,?,?)",(key,timestamp,encoded))
            elif table=="signals": self.db.execute("INSERT INTO signals(id,payload) VALUES(?,?)",(key,encoded))
            elif table=="forecasts": self.db.execute("INSERT INTO forecasts(id,origin_time,payload) VALUES(?,?,?)",(key,timestamp,encoded))
            elif table=="alerts": self.db.execute("INSERT INTO alerts(id,payload) VALUES(?,?)",(key,encoded))
            else: raise ValueError("unknown runtime persistence table")

    def observation(self,item: Observation)->None: self._insert("observations",str(item.observation_id),item.event_time.isoformat(),item.to_dict())
    def event(self,item: Event)->None: self._insert("events",str(item.event_id),item.event_time.isoformat(),asdict(item))
    def signal(self,item: Signal)->None: self._insert("signals",str(item.signal_id),"",asdict(item))
    def forecast(self,item: Forecast)->None: self._insert("forecasts",str(item.forecast_id),item.origin_time.isoformat(),asdict(item))

    def forecast_payload(self,prediction_id: str)->dict[str,Any]|None:
        with self._lock:
            row=self.db.execute("SELECT payload FROM forecasts WHERE id=?",(prediction_id,)).fetchone()
            return json.loads(row[0]) if row else None

    def alert(self,item: Alert)->None: self._insert("alerts",str(item.alert_id),"",asdict(item))

    def outcome(self,item: ForecastOutcome)->None:
        encoded=json.dumps(asdict(item),sort_keys=True,default=str); owns=False
        with self._lock:
            if not self.db.in_transaction: self.db.execute("BEGIN IMMEDIATE"); owns=True
            try:
                if self.db.execute("SELECT 1 FROM forecasts WHERE id=?",(item.prediction_id,)).fetchone() is None: raise ValueError("forecast must exist before recording its outcome")
                existing=self.db.execute("SELECT outcome_time,payload FROM outcomes WHERE prediction_id=? ORDER BY id LIMIT 1",(item.prediction_id,)).fetchone()
                if existing is not None:
                    if existing!=(item.outcome_time.isoformat(),encoded): raise RuntimeError("forecast outcome identity collision: existing outcome differs")
                    if owns: self.db.commit()
                    return
                self.db.execute("INSERT INTO outcomes(prediction_id,outcome_time,payload) VALUES(?,?,?)",(item.prediction_id,item.outcome_time.isoformat(),encoded))
                if owns: self.db.commit()
            except Exception:
                if owns: self.db.rollback()
                raise

    def response(self,item: ResponseRecord)->None:
        encoded=json.dumps(item.to_dict(),sort_keys=True,default=str)
        with self._lock:
            if self.db.execute("SELECT 1 FROM alerts WHERE id=?",(item.alert_id,)).fetchone() is None: raise ValueError("alert must exist before recording response")
            if item.prediction_id is not None and self.db.execute("SELECT 1 FROM forecasts WHERE id=?",(item.prediction_id,)).fetchone() is None: raise ValueError("prediction_id must reference a persisted forecast")
            existing=self.db.execute("SELECT payload FROM responses WHERE id=?",(item.response_id,)).fetchone()
            if existing is not None:
                if existing[0]!=encoded: raise RuntimeError("response identity collision: existing response differs")
                return
            self.db.execute("INSERT INTO responses(id,alert_id,decision_time,action_time,outcome_time,payload) VALUES(?,?,?,?,?,?)",(item.response_id,item.alert_id,item.decision_time.isoformat(),item.action_time.isoformat(),item.outcome_time.isoformat() if item.outcome_time else None,encoded))

    def snapshot(self)->dict[str,int]:
        with self._lock:
            return {"observations":self.db.execute("SELECT COUNT(*) FROM observations").fetchone()[0],"events":self.db.execute("SELECT COUNT(*) FROM events").fetchone()[0],"signals":self.db.execute("SELECT COUNT(*) FROM signals").fetchone()[0],"forecasts":self.db.execute("SELECT COUNT(*) FROM forecasts").fetchone()[0],"alerts":self.db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],"outcomes":self.db.execute("SELECT COUNT(*) FROM outcomes").fetchone()[0],"responses":self.db.execute("SELECT COUNT(*) FROM responses").fetchone()[0]}
