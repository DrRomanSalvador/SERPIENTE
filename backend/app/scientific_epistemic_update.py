"""Conservative epistemic updates produced by executed scientific work."""
from __future__ import annotations

from .scientific_discovery_engine import ScientificClaim, adversarial_update
from .scientific_work_execution import ExecutionOutcome, ScientificWorkResult


def update_claim_from_execution(claim: ScientificClaim, result: ScientificWorkResult) -> ScientificClaim:
    """Persist evidence without promoting an inconclusive result.

    Only an explicit rejected interpretation can demote a claim here. Executed
    or inconclusive work adds evidence but does not manufacture support for a
    stronger epistemic state.
    """
    if result.outcome == ExecutionOutcome.REJECTED:
        survived: bool | None = False
    else:
        survived = None
    return adversarial_update(
        claim,
        interpretation_survived=survived,
        evidence_ids=result.evidence,
    )


__all__ = ["update_claim_from_execution"]
