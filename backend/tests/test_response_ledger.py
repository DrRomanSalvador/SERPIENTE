from datetime import datetime, timedelta, timezone

import pytest

from app.response_ledger import CausalStatus, ResponseLedgerRecord, ResponseStatus, validate_response_payload


def window():
    start = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    return start, start + timedelta(hours=2)


def test_eligible_warning_without_response_is_explicitly_recordable():
    start, end = window()
    record = ResponseLedgerRecord(
        response_id="r1",
        alert_id="a1",
        prediction_id="p1",
        decision_id=None,
        decision_time=None,
        action_id=None,
        action_time=None,
        response_status=ResponseStatus.NO_RESPONSE,
        response_eligible=True,
        eligible_from=start,
        eligible_until=end,
        intended_mechanism="activate contingency review",
        response_delay_seconds=None,
        intervention_exposure=None,
        implementation_failure="no eligible decision recorded",
        resource_capacity_constraints="capacity unknown",
        outcome_id=None,
        outcome_time=None,
        response_horizon="2h",
        outcome_ascertainment_ref=None,
        counterfactual_ref=None,
        causal_status=CausalStatus.NOT_ASSESSED,
        provenance=("alert:a1",),
    )
    assert record.is_currently_eligible(start + timedelta(minutes=30))


def test_executed_response_requires_decision_and_action():
    start, end = window()
    with pytest.raises(ValueError, match="EXECUTED response requires"):
        ResponseLedgerRecord(
            response_id="r1", alert_id="a1", prediction_id="p1",
            decision_id=None, decision_time=None, action_id=None, action_time=None,
            response_status=ResponseStatus.EXECUTED, response_eligible=True,
            eligible_from=start, eligible_until=end, intended_mechanism="x",
            response_delay_seconds=None, intervention_exposure="none",
            implementation_failure=None, resource_capacity_constraints=None,
            outcome_id=None, outcome_time=None, response_horizon="2h",
            outcome_ascertainment_ref=None, counterfactual_ref=None,
            causal_status=CausalStatus.NOT_ASSESSED, provenance=("alert:a1",),
        )


def test_outcome_does_not_imply_causal_effect():
    start, end = window()
    with pytest.raises(ValueError, match="counterfactual"):
        ResponseLedgerRecord(
            response_id="r1", alert_id="a1", prediction_id="p1",
            decision_id="d1", decision_time=start, action_id="x1",
            action_time=start + timedelta(minutes=10),
            response_status=ResponseStatus.EXECUTED, response_eligible=True,
            eligible_from=start, eligible_until=end, intended_mechanism="x",
            response_delay_seconds=600, intervention_exposure="documented",
            implementation_failure=None, resource_capacity_constraints=None,
            outcome_id="o1", outcome_time=start + timedelta(hours=1), response_horizon="2h",
            outcome_ascertainment_ref="outcome:o1", counterfactual_ref=None,
            causal_status=CausalStatus.IDENTIFIED, provenance=("alert:a1",),
        )


def test_transport_round_trip_preserves_explicit_statuses():
    start, end = window()
    original = ResponseLedgerRecord(
        response_id="r1", alert_id="a1", prediction_id="p1", decision_id="d1",
        decision_time=start, action_id="x1", action_time=start + timedelta(minutes=10),
        response_status=ResponseStatus.EXECUTED, response_eligible=True,
        eligible_from=start, eligible_until=end, intended_mechanism="x",
        response_delay_seconds=600, intervention_exposure="documented",
        implementation_failure=None, resource_capacity_constraints=None,
        outcome_id="o1", outcome_time=start + timedelta(hours=1), response_horizon="2h",
        outcome_ascertainment_ref="outcome:o1", counterfactual_ref=None,
        causal_status=CausalStatus.DESCRIPTIVE_ONLY, provenance=("alert:a1",),
    )
    restored = validate_response_payload(original.to_dict())
    assert restored == original


def test_naive_transport_timestamp_is_rejected():
    start, end = window()
    payload = {
        "response_id": "r1", "alert_id": "a1", "response_status": "NO_RESPONSE",
        "response_eligible": True, "eligible_from": start.replace(tzinfo=None).isoformat(),
        "eligible_until": end.isoformat(), "intended_mechanism": "x",
        "response_horizon": "2h", "causal_status": "NOT_ASSESSED", "provenance": ["alert:a1"],
        "implementation_failure": "none",
    }
    with pytest.raises(ValueError, match="eligible_from"):
        validate_response_payload(payload)
