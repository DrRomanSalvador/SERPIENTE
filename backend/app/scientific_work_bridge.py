"""Bridge existing validation contracts into auditable ScientificWork candidates.

The bridge creates work; it does not execute validation or promote epistemic status.
Candidates remain subject to deduplication and admissibility before persistence.
"""
from __future__ import annotations

from .scientific_discovery_engine import ScientificWork, WorkStatus, admissible_work, deduplicate_work
from .scientific_validation_contracts import FalsificationCriterion, ValidationContract


def _criterion_work(
    contract: ValidationContract,
    criterion: FalsificationCriterion,
    *,
    index: int,
    decision_relevance: float,
    expected_information_gain: float,
    cost: float,
    owner: str,
) -> ScientificWork:
    work_id = f"{contract.contract_id}:{criterion.criterion_id}"
    return ScientificWork(
        work_id=work_id,
        trigger=f"validation-gap:{contract.component_id}",
        discovery=f"Validation criterion {criterion.criterion_id} is executable work for {contract.component_id}",
        scientific_question=criterion.hypothesis,
        current_knowledge=f"component={contract.component_id}; stage={contract.current_stage.value}; target={contract.target_stage.value}",
        uncertainty=f"criterion={criterion.criterion_id}; acceptance={criterion.acceptance_condition}",
        alternative_explanations=(
            "target failure reflects the hypothesized phenomenon",
            "target failure reflects measurement, temporal, or provenance error",
        ),
        affected_object=contract.component_id,
        mathematical_form=f"validation({contract.component_id}) -> {contract.target_stage.value}",
        assumptions=(contract.temporal_holdout, contract.calibration_requirement, contract.pit_requirement),
        identifiability="defined_by_validation_contract",
        data_required=criterion.required_data,
        temporal_requirements=(criterion.temporal_requirement, contract.temporal_holdout),
        falsification=(criterion.failure_condition,),
        benchmark=contract.benchmark_ids,
        validation=(
            *contract.metrics,
            contract.external_validation_requirement,
            contract.prospective_requirement,
        ),
        decision_relevance=decision_relevance,
        expected_information_gain=expected_information_gain,
        cost=cost,
        dependencies=(contract.contract_id,),
        owner=owner,
        status=WorkStatus.SPECIFIED,
        provenance=(*contract.provenance, criterion.provenance_requirement),
        stopping_rule=criterion.acceptance_condition,
        capability_not_authorized=(
            "prospective validity before prospective evidence",
            "causal effect inference from validation performance alone",
            "operational effectiveness before decision/outcome evaluation",
        ),
    )


def work_from_validation_contract(
    contract: ValidationContract,
    *,
    decision_relevance: float = 1.0,
    expected_information_gain: float = 1.0,
    cost: float = 1.0,
    owner: str = "ESPIA",
) -> tuple[ScientificWork, ...]:
    """Materialize validation criteria as deduplicated ScientificWork candidates."""
    candidates = tuple(
        _criterion_work(
            contract,
            criterion,
            index=index,
            decision_relevance=decision_relevance,
            expected_information_gain=expected_information_gain,
            cost=cost,
            owner=owner,
        )
        for index, criterion in enumerate(contract.falsification)
    )
    admissible = tuple(candidate for candidate in candidates if admissible_work(candidate))
    return deduplicate_work(admissible)


__all__ = ["work_from_validation_contract"]
