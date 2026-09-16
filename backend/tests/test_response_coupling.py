from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

import pytest

from app.contracts import Alert
from app.response import ResponseRecord
from app.storage import RuntimeStore


def _alert(alert_id="A1"):
    return Alert(alert_id=alert_id, level="HIGH", score=0.8, rationale=("test",), event_ids=("E1",), signal_ids=("S1",), forecast_ids=(), uncertainty=0.2, provenance=("source:test",))


def _response(**changes):
    t=datetime(2026,9,16,12,0,tzinfo=timezone.utc)
    values=dict(response_id="R1",alert_id="A1",prediction_id=None,decision_id="D1",decision_time=t,action_id="ACT1",action_time=t+timedelta(minutes=10),response_eligible=True,intended_mechanism="test response",response_delay_seconds=600.0,intervention_exposure="observed",implementation_failure=None,resource_capacity_constraints=None,outcome_id=None,outcome_time=None,response_horizon="24h",causal_status="NOT_ESTABLISHED",provenance=("test",))
    values.update(changes)
    return ResponseRecord(**values)


def test_response_requires_ordered_decision_action_and_persists(tmp_path: Path):
    store=RuntimeStore(tmp_path/"runtime.sqlite")
    with store.transaction(): store.alert(_alert())
    response=_response()
    with store.transaction(): store.response(response)
    assert store.snapshot()["responses"] == 1
    with store.transaction(): store.response(response)
    assert store.snapshot()["responses"] == 1
    store.close()


def test_response_rejects_action_before_decision():
    t=datetime(2026,9,16,12,0,tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        _response(decision_time=t, action_time=t-timedelta(seconds=1))


def test_response_rejects_unknown_alert(tmp_path: Path):
    store=RuntimeStore(tmp_path/"runtime.sqlite")
    with pytest.raises(ValueError): store.response(_response(alert_id="UNKNOWN"))
    store.close()
