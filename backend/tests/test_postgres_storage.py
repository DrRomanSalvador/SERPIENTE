import os
from datetime import datetime, timezone

import pytest

from app.contracts import Forecast, Observation
from app.outcomes import ForecastOutcome
from app.postgres_storage import PostgresRuntimeStore


@pytest.mark.skipif(not os.getenv("SERPIENTE_TEST_DATABASE_URL"), reason="PostgreSQL integration environment not configured")
def test_postgres_runtime_roundtrip_and_foreign_key():
    store = PostgresRuntimeStore(os.environ["SERPIENTE_TEST_DATABASE_URL"])
    now = datetime(2026,1,1,tzinfo=timezone.utc)
    observation = Observation("s","d","v","semantic","unit","Ceuta",now,now,now,"v1",0,1.0,("official",))
    forecast = Forecast("p1",now,"24h","risk",0.8,0.4,1.0,0.2,0.1,0.0,0.1,0.2,0.0,"STABLE",("official",),"a"*64)
    outcome = ForecastOutcome("p1",now,datetime(2026,1,2,tzinfo=timezone.utc),"risk",1,0.8,"24h",("official:outcome",))
    with store.transaction():
        store.observation(observation)
        store.forecast(forecast)
        store.outcome(outcome)
        store.outcome(outcome)
    assert store.forecast_payload("p1")["target"] == "risk"
    assert store.snapshot()["observations"] >= 1
    assert store.snapshot()["forecasts"] >= 1
    assert store.snapshot()["outcomes"] >= 1
    store.close()


@pytest.mark.skipif(not os.getenv("SERPIENTE_TEST_DATABASE_URL"), reason="PostgreSQL integration environment not configured")
def test_postgres_runtime_rejects_orphan_forecast_outcome():
    store = PostgresRuntimeStore(os.environ["SERPIENTE_TEST_DATABASE_URL"])
    outcome = ForecastOutcome("missing-forecast", datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 2, tzinfo=timezone.utc), "risk", 1, 0.8, "24h", ("official",))
    try:
        with pytest.raises(ValueError, match="forecast must exist"):
            store.outcome(outcome)
    finally:
        store.close()


@pytest.mark.skipif(not os.getenv("SERPIENTE_TEST_DATABASE_URL"), reason="PostgreSQL integration environment not configured")
def test_postgres_runtime_rejects_conflicting_outcome_retry():
    store = PostgresRuntimeStore(os.environ["SERPIENTE_TEST_DATABASE_URL"])
    now = datetime(2026,1,1,tzinfo=timezone.utc)
    forecast = Forecast("p-conflict", now, "24h", "risk", 0.8, 0.4, 1.0, 0.2, 0.1, 0.0, 0.1, 0.2, 0.0, "STABLE", ("official",), "b"*64)
    first = ForecastOutcome("p-conflict", now, datetime(2026,1,2,tzinfo=timezone.utc), "risk", 1, 0.8, "24h", ("official:outcome",))
    second = ForecastOutcome("p-conflict", now, datetime(2026,1,2,tzinfo=timezone.utc), "risk", 0, 0.8, "24h", ("official:outcome",))
    try:
        store.forecast(forecast)
        store.outcome(first)
        with pytest.raises(RuntimeError, match="identity collision"):
            store.outcome(second)
    finally:
        store.close()
