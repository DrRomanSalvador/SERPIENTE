from datetime import datetime, timezone

from app.outcomes import ForecastOutcome
from app.scientific_discovery_engine import ScientificWork, WorkStatus
from app.scientific_work_execution import ExecutionOutcome, execute_forecast_outcome_scoring

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = datetime(2026, 1, 2, tzinfo=timezone.utc)


def work() -> ScientificWork:
    return ScientificWork("W-OUTCOME-1", "forecast-outcome", "realized outcome became available", "how did the forecast score on this realized outcome?", "one realized pair", "calibration and generalization remain unresolved", ("idiosyncratic error", "systematic miscalibration"), "forecast", "Brier=(p-y)^2; logloss=-[y log p+(1-y)log(1-p)]", ("binary target",), "pairwise scoring identifiable", ("forecast", "outcome"), ("outcome_time >= origin_time",), ("pairwise score is reproducible",), ("paired baseline required",), ("aggregate scoring over eligible forecasts",), 1.0, 1.0, 1.0, (), "ESPIA", WorkStatus.SPECIFIED, ("test-fixture",), "score the pair exactly", ("calibration from one pair", "causal effect"))


def test_realized_pair_is_scored_but_not_promoted_to_validation():
    outcome = ForecastOutcome("pred-1", T0, T1, "event", 1, 0.75, "24h", ("outcome-source:1",))
    result = execute_forecast_outcome_scoring(work(), outcome)
    assert result.outcome == ExecutionOutcome.EXECUTED
    assert result.epistemic_state == "EVALUATED_OUTCOME"
    assert "brier=0.0625" in result.finding
    assert "log_loss" in result.finding
    assert "calibration" in result.finding
    assert result.new_work_required is False
