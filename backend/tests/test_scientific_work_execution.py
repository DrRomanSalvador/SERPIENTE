from datetime import datetime, timezone

from app.contracts import Forecast, Observation, Signal
from app.scientific_discovery_engine import ScientificWork, WorkStatus
from app.scientific_work_execution import ExecutionOutcome, execute_scientific_work


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
T2 = datetime(2026, 1, 3, tzinfo=timezone.utc)


def work() -> ScientificWork:
    return ScientificWork(
        work_id="W-EXEC-1",
        trigger="runtime",
        discovery="runtime object requires scientific execution",
        scientific_question="does the runtime object support the claimed interpretation?",
        current_knowledge="runtime contract only",
        uncertainty="observation process and future outcomes remain uncertain",
        alternative_explanations=("phenomenon change", "measurement-process change"),
        affected_object="runtime-object",
        mathematical_form="Y=g(S,O,D,R,C)+epsilon",
        assumptions=("provenance is available",),
        identifiability="partial",
        data_required=("runtime object",),
        temporal_requirements=("preserve declared timestamps",),
        falsification=("reject interpretation if discriminating evidence contradicts it",),
        benchmark=("declared runtime contract",),
        validation=("structural and temporal checks",),
        decision_relevance=1.0,
        expected_information_gain=1.0,
        cost=1.0,
        dependencies=(),
        owner="ESPIA",
        status=WorkStatus.SPECIFIED,
        provenance=("test-fixture",),
        stopping_rule="stop after structural checks are exhausted",
        capability_not_authorized=("causal effect", "prospective validity"),
    )


def test_observation_executes_without_overclaiming_phenomenon_change():
    obj = Observation(
        source_id="source",
        dataset_id="dataset",
        variable_id="cases",
        semantic_definition="observed cases",
        unit="count",
        geography="test",
        event_time=T0,
        publication_time=T1,
        acquisition_time=T2,
        source_version="v1",
        revision=0,
        value=10.0,
        provenance=("source:1",),
    )
    result = execute_scientific_work(work(), obj)
    assert result.outcome == ExecutionOutcome.INCONCLUSIVE
    assert result.epistemic_state == "OBSERVATION"
    assert result.new_work_required is True
    assert "cannot distinguish" in result.finding


def test_signal_execution_blocks_unsupported_temporal_inference():
    obj = Signal(
        signal_id="sig-1",
        event_id="event-1",
        domain="health",
        variable_id="cases",
        value=2.0,
        z_score=3.0,
        anomaly_score=0.9,
        trend=1.0,
        acceleration=0.2,
        volatility=0.3,
        provenance=("signal-source:1",),
    )
    result = execute_scientific_work(work(), obj)
    assert result.outcome == ExecutionOutcome.INCONCLUSIVE
    assert "no event timestamp" in result.finding


def test_forecast_execution_requires_future_outcome_for_scoring():
    obj = Forecast(
        forecast_id="fc-1",
        origin_time=T0,
        horizon="24h",
        target="event",
        probability=0.7,
        lower=0.2,
        upper=0.9,
        aleatoric=0.1,
        epistemic=0.1,
        measurement=0.1,
        parameter=0.1,
        structural=0.1,
        model_disagreement=0.1,
        regime="stable",
        provenance=("forecast-source:1",),
        point_in_time_fingerprint="pit-1",
    )
    result = execute_scientific_work(work(), obj)
    assert result.outcome == ExecutionOutcome.BLOCKED_EXTERNAL
    assert result.epistemic_state == "PREDICTION"
    assert "outcome" in result.finding


def test_invalid_observation_temporal_ordering_is_rejected_by_contract():
    try:
        Observation(
            source_id="source",
            dataset_id="dataset",
            variable_id="cases",
            semantic_definition="observed cases",
            unit="count",
            geography="test",
            event_time=T2,
            publication_time=T1,
            acquisition_time=T1,
            source_version="v1",
            revision=0,
            value=10.0,
            provenance=("source:1",),
        )
    except ValueError:
        return
    raise AssertionError("invalid temporal observation was accepted")
