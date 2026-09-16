from app.scientific_discovery_engine import KnowledgeState, ScientificClaim
from app.scientific_epistemic_update import update_claim_from_execution
from app.scientific_work_execution import ExecutionOutcome, ScientificWorkResult


def claim(state=KnowledgeState.HYPOTHESIS):
    return ScientificClaim("C-1", "the observed change reflects the underlying phenomenon", state, (), ("single runtime object",), ("test",), ("descriptive interpretation",), ("causal effect", "prospective validity"))


def result(outcome):
    return ScientificWorkResult("W-1", "R-1", outcome, "executed result", ("evidence:1",), "OBSERVATION", False, ("causal effect",), ("runtime:R-1",))


def test_inconclusive_execution_adds_traceable_evidence_without_promotion():
    updated = update_claim_from_execution(claim(), result(ExecutionOutcome.INCONCLUSIVE))
    assert updated.state == KnowledgeState.HYPOTHESIS
    assert updated.evidence_ids == ("execution:W-1:R-1",)


def test_rejected_execution_demotes_claim():
    updated = update_claim_from_execution(claim(), result(ExecutionOutcome.REJECTED))
    assert updated.state == KnowledgeState.REJECTED
    assert updated.evidence_ids == ("execution:W-1:R-1",)
