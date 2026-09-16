"""Conservative epistemic updates produced by executed scientific work."""
from __future__ import annotations

from .scientific_discovery_engine import ScientificClaim, adversarial_update
from .scientific_work_execution import ExecutionOutcome, ScientificWorkResult


def update_claim_from_execution(claim: ScientificClaim, result: ScientificWorkResult) -> ScientificClaim:
    """Persist one traceable execution evidence node without fake corroboration."""
    survived: bool | None = False if result.outcome == ExecutionOutcome.REJECTED else None
    evidence_id = f"execution:{result.work_id}:{result.runtime_id}"
    return adversarial_update(claim, interpretation_survived=survived, evidence_ids=(evidence_id,))


__all__ = ["update_claim_from_execution"]
