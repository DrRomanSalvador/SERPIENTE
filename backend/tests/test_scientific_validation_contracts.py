from __future__ import annotations

import pytest

from app.scientific_validation_contracts import (
    AlertLevel,
    DecisionLossContract,
    FalsificationCriterion,
    ValidationContract,
    ValidationStage,
)


def criterion() -> FalsificationCriterion:
    return FalsificationCriterion(
        "F1", "candidate adds predictive information", "blocked temporal comparison",
        "candidate loses against baseline", "candidate improves predefined metric",
        ("outcome", "candidate", "baseline"), "strict temporal holdout", "immutable PIT provenance",
    )


def test_validation_contract_encodes_falsification_and_future_evidence():
    contract = ValidationContract(
        "VC1", "interaction-x-y", ValidationStage.TESTED,
        ValidationStage.PROSPECTIVE_VALIDATION_REQUIRED, "rolling-origin",
        ("persistence", "seasonal"), ("brier", "log_loss"),
        "calibration assessed separately", "all features available by cutoff",
        "external cohort required", "prospective registration required", (criterion(),), ("spec-v1",),
    )
    assert contract.current_stage is ValidationStage.TESTED
    assert contract.falsification[0].failure_condition == "candidate loses against baseline"


def test_decision_loss_contract_rejects_negative_costs():
    with pytest.raises(ValueError):
        DecisionLossContract("D1", "decision", -1, 1, 1, 1, "p>c", "owner", "reversible", "expiry", ("x",))


def test_alert_levels_are_typed_and_ordered_semantically():
    assert AlertLevel.OBSERVATION.value.startswith("0_")
    assert AlertLevel.SIGNAL.value.startswith("1_")
    assert AlertLevel.CONDITIONAL_RISK.value.startswith("2_")
    assert AlertLevel.DECISION.value.startswith("3_")
    assert AlertLevel.EVALUATION.value.startswith("4_")


def test_falsification_requires_temporal_and_provenance_constraints():
    with pytest.raises(ValueError):
        FalsificationCriterion("F", "h", "test", "failure", "acceptance", ("x",), "", "provenance")
