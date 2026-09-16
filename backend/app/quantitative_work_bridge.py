"""Translate quantitative audit deficits into bounded ScientificWork candidates."""
from __future__ import annotations

from .quantitative_scientific_audit import QuantitativeMethodAudit
from .scientific_discovery_engine import ScientificWork, WorkStatus, deduplicate_work


def work_from_quantitative_audit(audit: QuantitativeMethodAudit, *, owner: str = "ESPIA") -> tuple[ScientificWork, ...]:
    """Create one candidate per material quantitative dimension lacking evidence.

    The bridge is deliberately conservative: it does not infer that a dimension
    is deficient merely because it exists. Callers supply audit fields that
    explicitly describe the unresolved requirement.
    """
    candidates: list[ScientificWork] = []
    dimensions = (
        ("identification", audit.identification.value, "resolve identification status"),
        ("uncertainty", "; ".join(audit.uncertainty), "quantify uncertainty"),
        ("sensitivity", "; ".join(audit.sensitivity), "execute sensitivity analysis"),
        ("robustness", "; ".join(audit.robustness), "test robustness"),
        ("validation", "; ".join(audit.validation), "execute validation design"),
    )
    for dimension, requirement, question_suffix in dimensions:
        candidates.append(
            ScientificWork(
                work_id=f"{audit.method_id}:{dimension}",
                trigger=f"quantitative-audit:{audit.method_id}:{dimension}",
                discovery=requirement,
                scientific_question=f"{audit.scientific_question}; {question_suffix}",
                current_knowledge=f"inference={audit.inference_type.value}; identification={audit.identification.value}",
                uncertainty=requirement,
                alternative_explanations=(
                    "the unresolved dimension reflects the hypothesized phenomenon",
                    "the unresolved dimension reflects observation, measurement, denominator, temporal, or model error",
                ),
                affected_object=audit.method_id,
                mathematical_form="audit -> falsifiable quantitative work",
                assumptions=audit.assumptions,
                identifiability=audit.identification.value,
                data_required=audit.predictor_definitions,
                temporal_requirements=("preserve information cutoff and outcome time",),
                falsification=audit.falsification,
                benchmark=audit.benchmarks,
                validation=audit.validation,
                decision_relevance=1.0,
                expected_information_gain=1.0,
                cost=1.0,
                dependencies=(audit.method_id,),
                owner=owner,
                status=WorkStatus.SPECIFIED,
                provenance=audit.provenance,
                stopping_rule=f"close {dimension} work only when its stated evidence requirement is satisfied or explicitly shown non-identifiable",
                capability_not_authorized=audit.capability_not_authorized,
            )
        )
    return deduplicate_work(candidates)


__all__ = ["work_from_quantitative_audit"]
