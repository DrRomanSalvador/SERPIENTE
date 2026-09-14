from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import Alert, Event, Forecast, Observation, Signal


class RuntimeStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self.db = sqlite3.connect(self.path, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS observations (id TEXT PRIMARY KEY, event_time TEXT NOT NULL, publication_time TEXT NOT NULL, acquisition_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, event_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS signals (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS forecasts (id TEXT PRIMARY KEY, origin_time TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_observations_event_time ON observations(event_time);
        CREATE INDEX IF NOT EXISTS idx_forecasts_origin_time ON forecasts(origin_time);
        """)
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(observations)")}
        if "publication_time" not in columns:
            self.db.execute("ALTER TABLE observations ADD COLUMN publication_time TEXT")
            self.db.execute("UPDATE observations SET publication_time = event_time WHERE publication_time IS NULL")
        if "acquisition_time" not in columns:
            self.db.execute("ALTER TABLE observations ADD COLUMN acquisition_time TEXT")
            self.db.execute("UPDATE observations SET acquisition_time = event_time WHERE acquisition_time IS NULL")

    def close(self) -> None:
        self.db.close()

    def _insert(self, table: str, key: str, timestamp: str, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, sort_keys=True, default=str)
        if table == "observations":
            self.db.execute("INSERT INTO observations(id,event_time,publication_time,acquisition_time,payload) VALUES(?,?,?,?,?)", (key, payload["event_time"], payload["publication_time"], payload["acquisition_time"], encoded))
        elif table == "events":
            self.db.execute("INSERT INTO events(id,event_time,payload) VALUES(?,?,?)", (key, timestamp, encoded))
        elif table == "forecasts":
            self.db.execute("INSERT INTO forecasts(id,origin_time,payload) VALUES(?,?,?)", (key, timestamp, encoded))
        else:
            self.db.execute(f"INSERT INTO {table}(id,payload) VALUES(?,?)", (key, encoded))

    def observation(self, item: Observation) -> None:
        self._insert("observations", str(item.observation_id), item.event_time.isoformat(), item.to_dict())

    def event(self, item: Event) -> None:
        self._insert("events", str(item.event_id), item.event_time.isoformat(), asdict(item))

    def signal(self, item: Signal) -> None:
        self._insert("signals", str(item.signal_id), "", asdict(item))

    def forecast(self, item: Forecast) -> None:
        self._insert("forecasts", str(item.forecast_id), item.origin_time.isoformat(), asdict(item))

    def alert(self, item: Alert) -> None:
        self._insert("alerts", str(item.alert_id), "", asdict(item))

    def snapshot(self) -> dict[str, int]:
        return {table: self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("observations", "events", "signals", "forecasts", "alerts")}
