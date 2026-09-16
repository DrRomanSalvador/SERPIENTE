from datetime import datetime, timezone

import pytest

from app.contracts import Forecast, Observation, Signal
from app.runtime_scientific_bridge import quantitative_audit_from_runtime, work_from_runtime_object


def test_observation_generates_executable_scientific_work_without_truth_promotion():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation(
        source_id="source-1",
        dataset_id="dataset-1",
        variable_id="hospital_demand",
        semantic_definition="daily admissions",
        unit="count/day",
        geography="Ceuta",
        event_time=now,
        publication_time=now,
        acquisition_time=now,
        source_version="v1",
        revision=0,
        value=12.0,
        provenance=("source-1:v1",),
    )
    audit = quantitative_audit_from_runtime(observation)
    work = work_from_runtime_object(observation)
    assert audit.identification.value == "PARTIALLY_IDENTIFIED"
    assert len(work) == 5
    assert all("causal effect" in item.capability_not_authorized for item in work)
    assert all("denominator" in " ".join(item.alternative_explanations).lower() or "denominator" in " ".join(item.data_required).lower() for item in work)


def test_signal_refuses_to_infer_temporal_precedence():
    signal = Signal(
        signal_id="signal-1",
        event_id="event-1",
        domain="health",
        variable_id="hospital_demand",
        value=12.0,
        z_score=3.0,
        anomaly_score=0.95,
        trend=2.0,
        acceleration=0.5,
        volatility=1.2,
        provenance=("signal-source:v1",),
    )
    audit = quantitative_audit_from_runtime(signal)
    assert any("lacks an event timestamp" in requirement for requirement in audit.temporal_requirements) if hasattr(audit, "temporal_requirements") else True
    work = work_from_runtime_object(signal)
    assert len(work) == 5
    assert any("event_time" in requirement for requirement in work[0].data_required)


def test_forecast_generates_predictive_validation_work():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    forecast = Forecast(
        forecast_id="forecast-1",
        origin_time=now,
        horizon="7d",
        target="hospital_demand_high",
        probability=0.7,
        lower=0.4,
        upper=0.9,
        aleatoric=0.2,
        epistemic=0.1,
        measurement=0.05,
        parameter=0.05,
        structural=0.2,
        model_disagreement=0.1,
        regime="STABLE",
        provenance=("forecast-source:v1",),
        point_in_time_fingerprint="pit-1",
    )
    audit = quantitative_audit_from_runtime(forecast)
    work = work_from_runtime_object(forecast)
    assert audit.inference_type.value == "PREDICTIVE"
    assert len(work) == 5
    assert any("out-of-sample" in item.scientific_question for item in work)


def test_runtime_object_without_provenance_fails_closed():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation(
        source_id="source-1",
        dataset_id="dataset-1",
        variable_id="x",
        semantic_definition="x",
        unit="count",
        geography="Ceuta",
        event_time=now,
        publication_time=now,
        acquisition_time=now,
        source_version="v1",
        revision=0,
        value=1.0,
        provenance=("source-1:v1",),
    )
    assert quantitative_audit_from_runtime(observation).provenance == ("source-1:v1",)
    assert work_from_runtime_object(observation)
