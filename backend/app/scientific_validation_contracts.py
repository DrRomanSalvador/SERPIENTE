"""Validation and falsification contracts for executable scientific components.

These objects define what evidence would move a component between epistemic
states. They do not manufacture that evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ValidationStage(StrEnum):
    IMPLEMENTED = "IMPLEMENTED"
    TESTED = "TESTED"
    RETROSPECTIVELY_EVALUATED = "RETROSPECTIVELY_EVALUATED"
    PROSPECTIVE_VALIDATION_REQUIRED = "PROSPECTIVE_VALIDATION_REQUIRED"
    PROSPECTIVELY_VALIDATED = "PROSPECTIVELY_VALIDATED"
    OPERATIONAL_VALIDATION_REQUIRED = "OPERATIONAL_VALIDATION_REQUIRED"


class AlertLevel(StrEnum):
    OBSERVATION = "0_OBSERVATION"
    SIGNAL = "1_SIGNAL"
    CONDITIONAL_RISK = "2_CONDITIONAL_RISK"
    DECISION = "3_DECISION"
    EVALUATION = "4_EVALUATION"


@dataclass(frozen=True, slots=True)
class FalsificationCriterion:
    criterion_id: str
    hypothesis: str
    test_definition: str
    failure_condition: str
    acceptance_condition: str
    required_data: tuple[str, ...]
    temporal_requirement: str
    provenance_requirement: str

    def __post_init__(self) -> None:
        required = (self.criterion_id, self.hypothesis, self.test_definition,
                    self.failure_condition, self.acceptance_condition,
                    self.temporal_requirement, self.provenance_requirement)
        if any(not value.strip() for value in required) or not self.required_data:
            raise ValueError("falsification criterion is incomplete")


@dataclass(frozen=True, slots=True)
class ValidationContract:
    contract_id: str
    component_id: str
    current_stage: ValidationStage
    target_stage: ValidationStage
    temporal_holdout: str
    benchmark_ids: tuple[str, ...]
    metrics: tuple[str, ...]
    calibration_requirement: str
    pit_requirement: str
    external_validation_requirement: str
    prospective_requirement: str
    falsification: tuple[FalsificationCriterion, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        required = (self.contract_id, self.component_id, self.temporal_holdout,
                    self.calibration_requirement, self.pit_requirement,
                    self.external_validation_requirement, self.prospective_requirement)
        if any(not value.strip() for value in required):
            raise ValueError("validation contract is incomplete")
        if not self.benchmark_ids or not self.metrics or not self.falsification or not self.provenance:
            raise ValueError("validation contract requires benchmarks, metrics, falsification and provenance")
        if self.target_stage.value == ValidationStage.PROSPECTIVELY_VALIDATED.value and not self.prospective_requirement.strip():
            raise ValueError("prospective validation target requires a prospective requirement")


@dataclass(frozen=True, slots=True)
class DecisionLossContract:
    contract_id: str
    decision_id: str
    false_positive_cost: float
    false_negative_cost: float
    action_cost: float
    harm_cost: float
    threshold_rule: str
    decision_owner: str
    reversibility: str
    expiry_rule: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        costs = (self.false_positive_cost, self.false_negative_cost, self.action_cost, self.harm_cost)
        if any(value < 0 for value in costs):
            raise ValueError("decision costs must be non-negative")
        required = (self.contract_id, self.decision_id, self.threshold_rule,
                    self.decision_owner, self.reversibility, self.expiry_rule)
        if any(not value.strip() for value in required) or not self.provenance:
            raise ValueError("decision loss contract is incomplete")


__all__ = ["AlertLevel", "DecisionLossContract", "FalsificationCriterion", "ValidationContract", "ValidationStage"]
