from datetime import datetime, timezone

from app.contracts import Forecast, Observation, Signal
from app.scientific_discovery_engine import ScientificWork, WorkStatus
from app.scientific_work_execution import ExecutionOutcome, execute_scientific_work

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
T2 = datetime(2026, 1, 3, tzinfo=timezone.utc)


def work() -> ScientificWork:
    return ScientificWork("W-EXEC-1", "runtime", "runtime object requires scientific execution", "does the runtime object support the claimed interpretation?", "runtime contract only", "observation process and future outcomes remain uncertain", ("phenomenon change", "measurement-process change"), "runtime-object", "Y=g(S,O,D,R,C)+epsilon", ("provenance is available",), "partial", ("runtime object",), ("preserve declared timestamps",), ("reject interpretation if discriminating evidence contradicts it",), ("declared runtime contract",), ("structural and temporal checks",), 1.0, 1.0, 1.0, (), "ESPIA", WorkStatus.SPECIFIED, ("test-fixture",), "stop after structural checks are exhausted", ("causal effect", "prospective validity"))


def test_observation_executes_without_overclaiming_phenomenon_change():
    obj = Observation("source", "dataset", "cases", "observed cases", "count", "test", T0, T1, T2, "v1", 0, 10.0, ("source:1",))
    result = execute_scientific_work(work(), obj)
    assert result.outcome == ExecutionOutcome.INCONCLUSIVE
    assert result.epistemic_state == "OBSERVATION"
    assert result.new_work_required is False
    assert "cannot distinguish" in result.finding


def test_signal_execution_blocks_unsupported_temporal_inference():
    obj = Signal("sig-1", "event-1", "health", "cases", 2.0, 3.0, 0.9, 1.0, 0.2, 0.3, ("signal-source:1",))
    result = execute_scientific_work(work(), obj)
    assert result.outcome == ExecutionOutcome.INCONCLUSIVE
    assert result.new_work_required is False
    assert "no event timestamp" in result.finding


def test_forecast_execution_requires_future_outcome_for_scoring():
    obj = Forecast("fc-1", T0, "24h", "event", 0.7, 0.2, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, "stable", ("forecast-source:1",), "pit-1")
    result = execute_scientific_work(work(), obj)
    assert result.outcome == ExecutionOutcome.BLOCKED_EXTERNAL
    assert result.new_work_required is False
    assert result.epistemic_state == "PREDICTION"
    assert "outcome" in result.finding


def test_invalid_observation_temporal_ordering_is_rejected_by_contract():
    try:
        Observation("source", "dataset", "cases", "observed cases", "count", "test", T2, T1, T1, "v1", 0, 10.0, ("source:1",))
    except ValueError:
        return
    raise AssertionError("invalid temporal observation was accepted")
