from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Iterable

import numpy as np
import pandas as pd

from .contracts import Observation


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    as_of: datetime
    values: dict[str, float]
    trends: dict[str, float]
    accelerations: dict[str, float]
    volatility: dict[str, float]
    lags: dict[str, tuple[float, ...]]
    interactions: dict[str, float]
    regime: str
    fingerprint: str


class PointInTimeStore:
    def __init__(self) -> None:
        self._rows: list[Observation] = []

    def add(self, observations: Iterable[Observation]) -> None:
        self._rows.extend(observations)
        self._rows.sort(key=lambda x: (x.event_time, x.acquisition_time, x.revision))

    def history_at(self, as_of: datetime) -> list[Observation]:
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        visible = [row for row in self._rows if row.known_at(as_of) and row.event_time <= as_of]
        latest: dict[tuple[str, str, str, str, datetime], Observation] = {}
        for row in visible:
            key = (row.source_id, row.dataset_id, row.variable_id, row.geography, row.event_time)
            previous = latest.get(key)
            if previous is None or (row.revision, row.acquisition_time) > (previous.revision, previous.acquisition_time):
                latest[key] = row
        return sorted(latest.values(), key=lambda x: (x.event_time, x.variable_id, x.source_id))

    def at(self, as_of: datetime) -> list[Observation]:
        history = self.history_at(as_of)
        latest: dict[tuple[str, str, str, str], Observation] = {}
        for row in history:
            key = (row.source_id, row.dataset_id, row.variable_id, row.geography)
            previous = latest.get(key)
            if previous is None or row.event_time > previous.event_time:
                latest[key] = row
        return list(latest.values())

    def fingerprint(self, as_of: datetime) -> str:
        rows = [r.to_dict() for r in self.history_at(as_of)]
        return sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()


class LongitudinalStateBuilder:
    def __init__(self, *, windows: tuple[int, ...] = (3, 7, 14), lags: tuple[int, ...] = (1, 2, 7)) -> None:
        if not windows or not lags or any(x <= 0 for x in (*windows, *lags)):
            raise ValueError("windows and lags must contain positive integers")
        self.windows = windows
        self.lags = lags

    @staticmethod
    def _deduplicate_same_time(rows: list[Observation]) -> list[Observation]:
        grouped: dict[tuple[str, datetime], list[Observation]] = {}
        for row in rows:
            if row.missing:
                continue
            grouped.setdefault((row.variable_id, row.event_time), []).append(row)
        result: list[Observation] = []
        for (variable, event_time), items in grouped.items():
            values = {float(item.value) for item in items if item.value is not None}
            if len(values) > 1:
                raise ValueError(f"conflicting observations for variable={variable} at event_time={event_time.isoformat()}")
            result.append(max(items, key=lambda item: (item.quality, item.revision, item.acquisition_time)))
        return sorted(result, key=lambda x: (x.event_time, x.variable_id))

    def build(self, observations: Iterable[Observation], *, as_of: datetime) -> StateSnapshot:
        rows = [r for r in observations if r.known_at(as_of) and r.event_time <= as_of and not r.missing]
        rows = self._deduplicate_same_time(rows)
        if not rows:
            raise ValueError("no non-missing point-in-time observations available")
        frame = pd.DataFrame([{"variable": r.variable_id, "event_time": r.event_time, "value": r.value} for r in rows])
        frame = frame.sort_values("event_time")
        values: dict[str, float] = {}
        trends: dict[str, float] = {}
        accelerations: dict[str, float] = {}
        volatility: dict[str, float] = {}
        lag_values: dict[str, tuple[float, ...]] = {}
        for variable, group in frame.groupby("variable", sort=True):
            series = group.set_index("event_time")["value"].astype(float).sort_index()
            if not np.isfinite(series.to_numpy()).all():
                raise ValueError("state contains non-finite values")
            values[variable] = float(series.iloc[-1])
            diff = series.diff().dropna()
            trends[variable] = float(diff.tail(self.windows[0]).mean()) if not diff.empty else 0.0
            acceleration = diff.diff().dropna()
            accelerations[variable] = float(acceleration.tail(self.windows[0]).mean()) if not acceleration.empty else 0.0
            recent_diff = diff.tail(self.windows[-1])
            std = float(recent_diff.std(ddof=1)) if len(recent_diff) > 1 else 0.0
            volatility[variable] = std if np.isfinite(std) else 0.0
            lag_values[variable] = tuple(float(series.iloc[-(lag + 1)]) for lag in self.lags if len(series) > lag)
        numeric = np.array(list(values.values()), dtype=float)
        if not np.isfinite(numeric).all():
            raise ValueError("state contains non-finite values")
        interactions: dict[str, float] = {}
        variables = sorted(values)
        for i, left in enumerate(variables):
            for right in variables[i + 1:]:
                value = values[left] * values[right]
                if not np.isfinite(value):
                    raise ValueError("state interaction is non-finite")
                interactions[f"{left}*{right}"] = float(value)
        regime = self._regime(frame)
        payload = {"as_of": as_of.astimezone(timezone.utc).isoformat(), "values": values, "trends": trends, "accelerations": accelerations, "volatility": volatility, "lags": lag_values, "interactions": interactions, "regime": regime}
        fingerprint = sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return StateSnapshot(as_of, values, trends, accelerations, volatility, lag_values, interactions, regime, fingerprint)

    @staticmethod
    def _regime(frame: pd.DataFrame) -> str:
        statuses: list[str] = []
        for _, group in frame.groupby("variable", sort=True):
            if len(group) < 8:
                continue
            values = group.sort_values("event_time")["value"].to_numpy(dtype=float)
            split = len(values) // 2
            a, b = values[:split], values[split:]
            if len(a) < 3 or len(b) < 3:
                continue
            std = float(np.std(values))
            if not np.isfinite(std):
                statuses.append("UNKNOWN")
                continue
            mean_shift = abs(float(b.mean() - a.mean())) / (std + 1e-12)
            variance_ratio = (float(np.var(b)) + 1e-12) / (float(np.var(a)) + 1e-12)
            statuses.append("SHIFT_DETECTED" if mean_shift >= 1.5 or variance_ratio >= 3.0 or variance_ratio <= 1 / 3.0 else "STABLE")
        if "SHIFT_DETECTED" in statuses:
            return "SHIFT_DETECTED"
        if "UNKNOWN" in statuses:
            return "UNKNOWN"
        return "STABLE" if statuses else "INSUFFICIENT_HISTORY"
