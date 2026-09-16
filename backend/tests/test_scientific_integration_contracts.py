from __future__ import annotations

import pytest

from app.scientific_integration_contracts import (
    BenchmarkContract,
    BenchmarkFamily,
    ModelChangeGate,
    ObservationProcessDescriptor,
    PointInTimePredictionContract,
    PredictionMetricDefinition,
)


def test_prediction_contract_preserves_point_in_time_identity():
    record = PointInTimePredictionContract(
        prediction_id="P1",
        information_cutoff="2026-09-16T10:00:00Z",
        observation_vintage="2026-09-16",
        feature_availability=(("x", "2026-09-16T09:59:00Z"),),
        forecast_origin="2026-09-16T10:00:00Z",
        forecast_horizon="24h",
        model_version="model-v1",
        target_definition="event",
        outcome_definition="event observed by horizon",
        point_in_time_fingerprint="pit-1",
        provenance=("obs-1",),
    )
    assert record.point_in_time_fingerprint == "pit-1"
    assert record.feature_availability[0][0] == "x"


def test_benchmark_exclusion_requires_reason():
    with pytest.raises(ValueError):
        BenchmarkContract("B1", BenchmarkFamily.HIERARCHICAL_MODEL, "target", "24h", "EXCLUDED")


def test_metric_definition_must_state_question_and_limitations():
    metric = PredictionMetricDefinition("brier", "What probabilistic accuracy?", "miscalibration", "does not establish causality")
    assert metric.metric_id == "brier"


def test_model_deployment_requires_validation_and_approval():
    with pytest.raises(ValueError):
        ModelChangeGate("m", "1", "2", "train", "validation", ("B1",), False, None, True, "rollback")


def test_observation_process_keeps_denominator_and_measurement_process():
    descriptor = ObservationProcessDescriptor(
        "cases", "observed cases", "clinical ascertainment", "population_present",
        "partial", "selection", "reporting", "daily", "official-source",
    )
    assert descriptor.denominator == "population_present"
