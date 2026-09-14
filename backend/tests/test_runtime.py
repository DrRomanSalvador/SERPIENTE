from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from app.ceutia_boundary import prediction_to_ceutia
from app.contracts import Observation
from app.ingestion import CSVObservationAdapter, JSONObservationAdapter
from app.longitudinal import LongitudinalStateBuilder, PointInTimeStore
from app.prediction import LongitudinalForecaster
from app.runtime import SerpienteRuntime
from app.storage import RuntimeStore
from app.validation import calibration_report, multidomain_incremental_value, numerical_adversarial_check, temporal_leakage_check


def obs(i, *, value=1.0, variable="risk", acquired=None, revision=0):
    t = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=i)
    acquired = acquired or t + timedelta(hours=1)
    return Observation("source", "dataset", variable, "test semantic", "unit", "Ceuta", t, t, acquired, "v1", revision, value, (f"source:source",))


def test_contract_rejects_nonfinite_and_missing_sentinel():
    with pytest.raises(ValueError): obs(0, value=float("nan"))
    with pytest.raises(ValueError):
        Observation("s", "d", "v", "semantic", "u", "g", datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc), "v1", 0, 0.0, ("s",), missing=True)


def test_point_in_time_replay_excludes_future_and_selects_revision():
    store = PointInTimeStore(); t = datetime(2026, 1, 10, tzinfo=timezone.utc)
    store.add([obs(1, value=1), obs(2, value=2), obs(3, value=3, acquired=datetime(2026, 1, 20, tzinfo=timezone.utc))])
    visible = store.at(t)
    assert all(row.event_time <= t for row in visible)
    assert len(visible) == 1


def test_state_contains_lags_trends_and_regime():
    rows = [obs(i, value=float(i)) for i in range(12)]
    state = LongitudinalStateBuilder().build(rows, as_of=rows[-1].event_time + timedelta(hours=2))
    assert state.lags["risk"][0] == 10.0
    assert state.trends["risk"] > 0
    assert state.accelerations["risk"] == 0
    assert state.regime in {"STABLE", "SHIFT_DETECTED"}


def test_runtime_executes_event_signal_pattern_trajectory_alert_and_persists(tmp_path):
    store = RuntimeStore(tmp_path / "runtime.sqlite")
    runtime = SerpienteRuntime(store=store)
    rows = [obs(i, value=float(i + 1)) for i in range(12)]
    runtime.ingest(rows)
    result = runtime.process(as_of=rows[-1].event_time + timedelta(hours=2), geography="Ceuta", domain="test", event_type="STATE_CHANGE")
    counts = store.snapshot(); store.close()
    assert result.alert.level in {"BASELINE", "ATTENTION", "WARNING", "DANGER", "CRITICAL"}
    assert counts["observations"] == 12 and counts["events"] == 1 and counts["signals"] == 1 and counts["alerts"] == 1


def test_forecaster_requires_temporal_holdout_and_produces_calibrated_prediction():
    n = 60
    frame = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="D", tz="UTC"), "x": np.arange(n, dtype=float), "target": (np.arange(n) % 3 == 0).astype(int)})
    model = LongitudinalForecaster(); report = model.fit(frame)
    assert report.temporal_order_valid and report.test_rows > 0
    pred = model.predict_probability(frame[["x"]].tail(5)); assert np.isfinite(pred).all() and ((pred >= 0) & (pred <= 1)).all()


def test_forecaster_rejects_explicit_future_columns():
    frame = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=40, freq="D", tz="UTC"), "future_target": np.arange(40), "target": np.arange(40) % 2})
    with pytest.raises(ValueError): LongitudinalForecaster().fit(frame)


def test_scientific_validation_rejects_future_information():
    frame = pd.DataFrame({"time": ["2026-01-02"], "target_time": ["2026-01-01"]})
    finding = temporal_leakage_check(frame); assert not finding.passed
    assert not numerical_adversarial_check([1.0, float("nan")]).passed


def test_calibration_and_multidomain_comparison_preserve_negative_results():
    report = calibration_report([0, 1, 1, 0], [0.2, 0.8, 0.7, 0.3]); assert 0 <= report["brier"] <= 1
    result = multidomain_incremental_value({"naive": {"brier": .2}, "single_domain": {"brier": .18}, "multidomain": {"brier": .25}})
    assert result["improves_brier"] is False


def test_adapters_preserve_metadata():
    payload = [{"variable_id":"v","semantic_definition":"semantic","unit":"u","geography":"Ceuta","event_time":"2026-01-01T00:00:00+00:00","publication_time":"2026-01-01T00:00:00+00:00","acquisition_time":"2026-01-01T01:00:00+00:00","source_version":"1","revision":0,"value":2.0,"provenance":["official"]}]
    rows = JSONObservationAdapter().ingest(__import__("json").dumps(payload), metadata={"source_id":"s","dataset_id":"d"}); assert rows[0].source_id == "s"
    csv = "variable_id,semantic_definition,unit,geography,event_time,publication_time,acquisition_time,source_version,revision,value,provenance\nv,semantic,u,Ceuta,2026-01-01T00:00:00+00:00,2026-01-01T00:00:00+00:00,2026-01-01T01:00:00+00:00,1,0,2.0,official\n"
    rows = CSVObservationAdapter().ingest(csv, metadata={"source_id":"s","dataset_id":"d"}); assert rows[0].dataset_id == "d"


def test_ceutia_boundary_requires_provenance():
    rows = [obs(i, value=float(i + 1)) for i in range(12)]
    runtime = SerpienteRuntime(); runtime.ingest(rows)
    runtime.train(pd.DataFrame({"time": pd.date_range("2026-01-01", periods=40, freq="D", tz="UTC"), "x": np.arange(40, dtype=float), "target": (np.arange(40) % 2).astype(int)}))
    forecast = runtime.forecast(pd.DataFrame({"x": [39.0]}), origin_time=rows[-1].event_time + timedelta(hours=2), target="risk", horizon="24h", regime="STABLE", provenance=("official",))
    envelope = prediction_to_ceutia(forecast); assert envelope.canonical_hash()
