from datetime import datetime, timezone

from app.outcomes import ForecastOutcome
from app.scientific_discovery_engine import ScientificWork, WorkStatus
from app.scientific_work_execution import ExecutionOutcome, execute_forecast_outcome_scoring


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = datetime(2026, 1, 2, tzinfo=timezone.utc)


def work() -> ScientificWork:
    return ScientificWork(
        work_id="W-OUTCOME-1",
        trigger="forecast-outcome",
        discovery="realized outcome became available",
        scientific_question="how did the forecast score on this realized outcome?",
        current_knowledge="one realized pair",
        uncertainty="calibration and generalization remain unresolved",
        alternative_explanations=("forecast error is idiosyncratic", "forecast error reflects systematic miscalibration"),
        affected_object="forecast",
        mathematical_form="Brier=(p-y)^2; logloss=-[y log p+(1-y)log(1-p)]",
        assumptions=("binary target",),
        identifiability="pairwise scoring identifiable",
        data_required=("forecast", "outcome"),
        temporal_requirements=("outcome_time >= origin_time",),
        falsification=("pairwise score is exactly reproducible from forecast and outcome",),
        benchmark=("paired baseline required for incremental value",),
        validation=("aggregate scoring over eligible forecasts",),
        decision_relevance=1.0,
        expected_information_gain=1.0,
        cost=1.0,
        dependencies=(),
        owner="ESPIA",
        status=WorkStatus.SPECIFIED,
        provenance=("test-fixture",),
        stopping_rule="score the pair exactly",
        capability_not_authorized=("calibration from one pair", "causal effect"),
    )


def test_realized_pair_is_scored_but_not_promoted_to_validation():
    outcome = ForecastOutcome(
        prediction_id="pred-1",
        origin_time=T0,
        outcome_time=T1,
        target="event",
        observed=1,
        predicted_probability=0.75,
        horizon="24h",
        provenance=("outcome-source:1",),
    )
    result = execute_forecast_outcome_scoring(work(), outcome)
    assert result.outcome == ExecutionOutcome.EXECUTED
    assert result.epistemic_state == "EVALUATED_OUTCOME"
    assert "brier=0.0625" in result.finding
    assert "log_loss" in result.finding
    assert "calibration" in result.finding
    assert result.new_work_required is True
