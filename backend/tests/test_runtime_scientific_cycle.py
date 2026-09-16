from datetime import datetime, timezone

from app.contracts import Observation
from app.runtime_scientific_bridge import execute_runtime_scientific_cycle
from app.scientific_work_execution import ExecutionOutcome


def test_runtime_cycle_executes_generated_work_and_updates_epistemic_state():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation("source-1", "dataset-1", "hospital_demand", "daily admissions", "count/day", "Ceuta", now, now, now, "v1", 0, 12.0, ("source-1:v1",))
    results, claim = execute_runtime_scientific_cycle(observation)
    assert len(results) == 5
    assert all(result.runtime_id == str(observation.observation_id) for result in results)
    assert all(result.new_work_required is False for result in results)
    assert claim.state.value == "OBSERVATION"
    assert len(claim.evidence_ids) == 6
    assert all(result.outcome == ExecutionOutcome.INCONCLUSIVE for result in results)


def test_runtime_cycle_never_promotes_observation_to_causality():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation("source-1", "dataset-1", "x", "x", "count", "Ceuta", now, now, now, "v1", 0, 1.0, ("source-1:v1",))
    _, claim = execute_runtime_scientific_cycle(observation)
    assert claim.state.value == "OBSERVATION"
    assert "causal effect" in claim.capability_not_authorized
