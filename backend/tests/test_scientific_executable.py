from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from app.scientific_executable import (
    AlertContract,
    DynamicCoupling,
    EpistemicStatus,
    InterventionRecord,
    InterventionStatus,
    LaggedRelation,
    LatentState,
    ObservationProcess,
    OutcomeEvaluation,
    OutcomeFailure,
    ScientificVariable,
    StateTransition,
    UncertaintyDecomposition,
    VariableKind,
    brier_score,
    compare_forecasts,
    crps_ensemble,
    distributed_lag,
    interval_coverage,
    lagged_values,
    linear_state_transition,
    linear_trend_forecast,
    log_loss,
    observation_projection,
    persistence_forecast,
    rolling_change,
    seasonal_mean_forecast,
)


T0 = datetime(2026, 9, 16, 10, tzinfo=timezone.utc)


def test_linear_state_transition_matches_equation():
    result = linear_state_transition(
        [1.0, 2.0], [3.0], [4.0],
        np.eye(2), np.array([[2.0], [1.0]]), np.array([[1.0], [3.0]]),
        [0.5, -0.5],
    )
    assert result.next_state == (9.5, 14.5)


def test_state_transition_rejects_bad_dimensions():
    with pytest.raises(ValueError):
        linear_state_transition([1.0], [1.0], [1.0], np.eye(2), np.ones((2, 1)), np.ones((2, 1)))


def test_observation_projection_is_explicit_measurement_map():
    assert np.allclose(observation_projection([2.0, 3.0], [[1.0, 0.0], [0.0, 2.0]], [1.0, -1.0]), [3.0, 5.0])


def test_inferred_or_latent_state_cannot_become_observation_by_type():
    latent = ScientificVariable("s", VariableKind.LATENT, "index", "latent state", ("model-v1",))
    observed = ScientificVariable("y", VariableKind.OBSERVED, "count", "observed count", ("source-v1",))
    assert latent.kind is VariableKind.LATENT
    assert observed.kind is VariableKind.OBSERVED
    assert latent.kind != observed.kind


def test_latent_state_requires_uncertainty_dimension_and_provenance():
    state = LatentState("s1", T0, (1.0, 2.0), (0.1, 0.2), "state-v1", ("obs-1",))
    assert state.status is EpistemicStatus.IMPLEMENTED_NOT_VALIDATED
    with pytest.raises(ValueError):
        LatentState("s1", T0, (1.0,), (0.1, 0.2), "state-v1", ("obs-1",))


def test_observation_process_requires_all_measurement_layers():
    process = ObservationProcess("op1", "lab", "reporting", "present", "clinical", "0.8", "1d", "v2", "unknown", ("src-v1",))
    assert process.denominator == "present"
    with pytest.raises(ValueError):
        ObservationProcess("op1", "", "reporting", "present", "clinical", "0.8", "1d", "v2", "unknown", ("src-v1",))


def test_lag_and_distributed_lag_preserve_temporal_direction():
    assert np.array_equal(lagged_values([1, 2, 3, 4], 1), [1, 2, 3])
    assert np.array_equal(distributed_lag([1, 2, 3, 4], [0, 1], [0.5, 0.5]), [1.5, 2.5, 3.5])
    with pytest.raises(ValueError):
        lagged_values([1, 2], -1)


def test_dynamic_coupling_allows_time_varying_relation_without_causal_claim():
    a = DynamicCoupling("x", "y", T0, 0.2, 0.1, "rolling-regression-v1", T0, None, ("fit-1",))
    b = DynamicCoupling("x", "y", T0.replace(hour=11), 0.8, 0.2, "rolling-regression-v1", T0.replace(hour=11), None, ("fit-2",))
    assert a.coefficient != b.coefficient
    relation = LaggedRelation("r1", "x", "y", "x->y", (1, 2), "Ceuta", "daily", "hypothesized", ("ev1",), "NON_CAUSAL", "reporting", ("src",))
    assert relation.causal_status == "NON_CAUSAL"


def test_uncertainty_is_decomposed_and_non_negative():
    u = UncertaintyDecomposition(measurement=1, parameter=2, model=3, process=4, observation=5, structural=6, forecast=7, provenance=("model-v1",))
    assert u.total_variance_proxy == 28
    with pytest.raises(ValueError):
        UncertaintyDecomposition(measurement=-1, provenance=("model-v1",))


def test_probabilistic_metrics_are_distinct_computable_contracts():
    y = [0, 1, 1, 0]
    p = [0.1, 0.8, 0.7, 0.2]
    assert brier_score(y, p) < 0.1
    assert log_loss(y, p) > 0
    assert 0 <= interval_coverage([0, 1, 2], [-1, 0, 1], [1, 2, 3]) <= 1
    assert crps_ensemble([1.0, 2.0], [[0.5, 1.5], [1.5, 2.5]]) >= 0


def test_forecast_comparison_answers_incremental_value_against_baseline():
    evaluation = compare_forecasts([0, 1, 1, 0], [0.2, 0.6, 0.6, 0.2], [0.1, 0.9, 0.8, 0.1], metric=brier_score, metric_name="brier")
    assert evaluation.candidate_score < evaluation.baseline_score
    assert evaluation.candidate_improves
    assert evaluation.validation_status is EpistemicStatus.IMPLEMENTED_NOT_VALIDATED


def test_benchmark_primitives_are_deterministic_and_have_boundary_checks():
    assert np.array_equal(persistence_forecast([1, 2, 3], 2), [3, 3])
    assert np.array_equal(seasonal_mean_forecast([1, 2, 3, 4], 2, 2), [3.5, 3.5])
    assert len(linear_trend_forecast([1, 2, 3], 2)) == 2
    with pytest.raises(ValueError):
        persistence_forecast([], 1)


def test_change_detector_separates_mean_variance_and_autocorrelation_change():
    result = rolling_change([1, 1, 1, 1, 1, 2, 3, 4, 5, 6], 5)
    assert set(result) == {"delta_mean", "delta_variance", "delta_autocorrelation"}
    assert result["delta_mean"] > 0


def test_alert_requires_alternative_explanations_and_measurement_check():
    alert = AlertContract(
        "A1", T0, T0, "phenomenon", "Ceuta", "population-present", "24h", "rule-v1",
        0.1, "Bernoulli-v1", "NOT_CALIBRATED", ("e1",), ("reporting-change",),
        "CHECKED", "measurement+model", "owner", ("reversible-action",), ("burden",), "escalate-v1", T0.replace(hour=12), "outcome-v1",
    )
    assert alert.alert_id == "A1"
    with pytest.raises(ValueError):
        AlertContract(
            "A2", T0, T0, "phenomenon", "Ceuta", "population-present", "24h", "rule-v1",
            0.1, "Bernoulli-v1", "NOT_CALIBRATED", ("e1",), (), "CHECKED", "u", "owner", (), (), "e", T0.replace(hour=12), "outcome",
        )


def test_intervention_is_separate_from_prediction_and_outcome():
    intervention = InterventionRecord("I1", InterventionStatus.EXECUTED, T0, "exposed", "action", "expected", "O1", "counterfactual-required", ("alert-1",))
    outcome = OutcomeEvaluation("P1", "O1", OutcomeFailure.INTERVENTION, "observed", "definition-v1", "COMPLETE", ("outcome-source-v1",))
    assert intervention.status is InterventionStatus.EXECUTED
    assert outcome.failure_class is OutcomeFailure.INTERVENTION
    with pytest.raises(ValueError):
        InterventionRecord("I2", InterventionStatus.EXECUTED, None, "exposed", "action", "expected", None, "required", ("x",))


def test_persistence_of_status_does_not_claim_validation():
    state = LatentState("s", T0, (1.0,), (0.1,), "v1", ("x",))
    assert state.status.value == "IMPLEMENTED_NOT_VALIDATED"
