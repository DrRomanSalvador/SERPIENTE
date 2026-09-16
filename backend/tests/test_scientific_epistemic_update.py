from app.scientific_discovery_engine import KnowledgeState, ScientificClaim
from app.scientific_epistemic_update import update_claim_from_execution
from app.scientific_work_execution import ExecutionOutcome, ScientificWorkResult


def claim(state=KnowledgeState.HYPOTHESIS):
    return ScientificClaim(
        claim_id="C-1",
        statement="the observed change reflects the underlying phenomenon",
        state=state,
        evidence_ids=(),
        assumptions=("single runtime object",),
        provenance=("test",),
        capability_authorized=("descriptive interpretation",),
        capability_not_authorized=("causal effect", "prospective validity"),
    )


def result(outcome):
    return ScientificWorkResult(
        work_id="W-1",
        runtime_id="R-1",
        outcome=outcome,
        finding="executed result",
        evidence=("evidence:1",),
        epistemic_state="OBSERVATION",
        new_work_required=True,
        capability_not_authorized=("causal effect",),
        provenance=("runtime:R-1",),
    )


def test_inconclusive_execution_adds_evidence_without_promotion():
    updated = update_claim_from_execution(claim(), result(ExecutionOutcome.INCONCLUSIVE))
    assert updated.state == KnowledgeState.HYPOTHESIS
    assert updated.evidence_ids == ("evidence:1",)


def test_rejected_execution_demotes_claim():
    updated = update_claim_from_execution(claim(), result(ExecutionOutcome.REJECTED))
    assert updated.state == KnowledgeState.REJECTED
    assert updated.evidence_ids == ("evidence:1",)
