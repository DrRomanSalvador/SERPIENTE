from datetime import datetime, timezone

from app.contracts import Forecast
from app.outcomes import ForecastOutcome
from app.runtime import SerpienteRuntime
from app.storage import RuntimeStore


def test_realized_outcome_is_scored_and_persisted_as_scientific_execution(tmp_path):
    store = RuntimeStore(tmp_path / "forecast.sqlite")
    runtime = SerpienteRuntime(store=store)
    now = datetime(2026, 9, 16, 10, tzinfo=timezone.utc)
    forecast = Forecast("forecast-1", now, "24h", "event", 0.75, 0.2, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, "stable", ("forecast-source:v1",), "pit-1")
    store.forecast(forecast)
    outcome = ForecastOutcome("forecast-1", now, now.replace(hour=12), "event", 1, 0.75, "24h", ("outcome-source:v1",))
    result = runtime.record_outcome(outcome)
    assert result.epistemic_state == "EVALUATED_OUTCOME"
    assert result.outcome.value == "EXECUTED"
    assert "calibration" in result.finding
    snapshot = store.snapshot()
    assert snapshot["outcomes"] == 1
    assert snapshot["scientific_results"] == 1
    store.close()
