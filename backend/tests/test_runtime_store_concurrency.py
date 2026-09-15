from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from app.contracts import Forecast, Observation
from app.outcomes import ForecastOutcome
from app.storage import RuntimeStore


def _observation(i: int) -> Observation:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i)
    return Observation(
        "concurrency-source",
        "concurrency-dataset",
        "risk",
        "concurrency regression",
        "unit",
        "Ceuta",
        timestamp,
        timestamp,
        timestamp,
        "v1",
        0,
        float(i),
        ("official:concurrency",),
    )


def test_runtime_store_serializes_shared_connection_reads_and_writes(tmp_path):
    store = RuntimeStore(tmp_path / "concurrency.sqlite")
    observations = [_observation(i) for i in range(64)]

    def write(item: Observation) -> None:
        store.observation(item)

    def read() -> int:
        return store.snapshot()["observations"]

    try:
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(write, item) for item in observations]
            futures.extend(executor.submit(read) for _ in range(64))
            for future in futures:
                future.result()

        assert store.snapshot()["observations"] == len(observations)
    finally:
        store.close()


def test_runtime_store_rejects_orphan_forecast_outcome(tmp_path):
    store = RuntimeStore(tmp_path / "outcome-integrity.sqlite")
    outcome = ForecastOutcome(
        "missing-forecast",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        "risk",
        1,
        0.8,
        "24h",
        ("official:outcome",),
    )
    try:
        with pytest.raises(ValueError, match="forecast must exist"):
            store.outcome(outcome)
    finally:
        store.close()


def test_runtime_store_accepts_outcome_for_existing_forecast(tmp_path):
    store = RuntimeStore(tmp_path / "outcome-integrity-valid.sqlite")
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    forecast = Forecast("forecast-1", now, "24h", "risk", 0.8, 0.4, 1.0, 0.2, 0.1, 0.0, 0.1, 0.2, 0.0, "STABLE", ("official",), "a" * 64)
    outcome = ForecastOutcome("forecast-1", now, now + timedelta(days=1), "risk", 1, 0.8, "24h", ("official:outcome",))
    try:
        store.forecast(forecast)
        store.outcome(outcome)
        assert store.snapshot()["outcomes"] == 1
    finally:
        store.close()
