from datetime import datetime, timezone

import pytest

from app.scientific_discovery_engine import (
    AlternativeExplanation,
    FalsificationTask,
    KnowledgeState,
    ScientificClaim,
    ScientificWork,
    WorkStatus,
    admissible_work,
    adversarial_update,
    can_promote,
    deduplicate_work,
    prioritize_work,
    scientific_impact_map,
)


def claim(state=KnowledgeState.ASSOCIATION):
    return ScientificClaim(
        claim_id="c1",
        statement="X is associated with Y",
        state=state,
        evidence_ids=("e1",),
        assumptions=("stable measurement",),
        provenance=("source:e1",),
        capability_authorized=("specified forecasting",),
        capability_not_authorized=("causal intervention",),
    )


def work(work_id="w1", **overrides):
    base = dict(
        work_id=work_id,
        trigger="contradiction",
        discovery="new discrepancy",
        scientific_question="which process changed?",
        current_knowledge="association only",
        uncertainty="observation process",
        alternative_explanations=("state change", "reporting change"),
        affected_object="risk estimate",
        mathematical_form="Y=g(S,O,D)+eta",
        assumptions=("time ordering",),
        identifiability="partial",
        data_required=("versioned observations",),
        temporal_requirements=("point-in-time",),
        falsification=("source replacement test",),
        benchmark=("persistence",),
        validation=("blocked temporal evaluation",),
        decision_relevance=1.0,
        expected_information_gain=1.0,
        cost=1.0,
        dependencies=(),
        owner="ESPIA",
        status=WorkStatus.DISCOVERED,
        provenance=("claim:c1",),
        stopping_rule="stop when hypotheses are discriminated",
        capability_not_authorized=("causal claim",),
    )
    base.update(overrides)
    return ScientificWork(**base)


def test_claim_requires_authorization_boundary():
    with pytest.raises(ValueError):
        ScientificClaim("c1", "x", KnowledgeState.HYPOTHESIS, (), (), ("p",), ("a",), ())


def test_adversarial_failure_rejects_claim():
    updated = adversarial_update(claim(), interpretation_survived=False, evidence_ids=("adv1",))
    assert updated.state is KnowledgeState.REJECTED
    assert "adv1" in updated.evidence_ids


def test_adversarial_inconclusive_preserves_claim():
    updated = adversarial_update(claim(), interpretation_survived=None)
    assert updated == claim()


def test_causal_promotion_is_blocked_even_with_criterion():
    assert not can_promote(KnowledgeState.ASSOCIATION, KnowledgeState.CAUSAL_EFFECT, criterion_satisfied=True)


def test_epistemic_jump_to_established_is_blocked():
    assert not can_promote(KnowledgeState.UNKNOWN, KnowledgeState.ESTABLISHED, criterion_satisfied=True)
    assert not can_promote(KnowledgeState.OBSERVATION, KnowledgeState.CAUSAL_EFFECT, criterion_satisfied=True)
    assert can_promote(KnowledgeState.REPLICATED, KnowledgeState.ESTABLISHED, criterion_satisfied=True)


def test_work_priority_is_voi_like_not_task_count():
    low = work(work_id="w-low", decision_relevance=1, expected_information_gain=1, cost=10)
    high = work(work_id="w-high", decision_relevance=2, expected_information_gain=4, cost=1)
    assert prioritize_work((low, high))[0].work_id == "w-high"


def test_duplicate_work_ids_do_not_create_new_semantic_work():
    first = work("w1")
    duplicate = work("w2")
    unique = work("w3", scientific_question="does the denominator drift explain the signal?")
    result = deduplicate_work((first, duplicate, unique))
    assert tuple(w.work_id for w in result) == ("w1", "w3")


def test_work_admissibility_requires_core_scientific_controls():
    assert admissible_work(work())
    assert not admissible_work(work(alternative_explanations=()))
    assert not admissible_work(work(falsification=()))
    assert not admissible_work(work(benchmark=()))
    assert not admissible_work(work(validation=()))
    assert not admissible_work(work(provenance=()))
    assert not admissible_work(work(capability_not_authorized=()))


def test_impact_map_is_scoped_to_claim():
    alt = AlternativeExplanation("a1", "c1", "reporting changed", ("reporting intensity",), ("stable state",), ("p",))
    task = FalsificationTask("t1", "c1", "compare source process", "claim fails", "stop after preregistered test", ("source data",), "PIT", "source-version")
    other = FalsificationTask("t2", "other", "irrelevant", "x", "stop", ("x",), "PIT", "p")
    result = scientific_impact_map(claim(), (alt,), (task, other))
    assert result["alternatives"] == ("a1",)
    assert result["falsification_tasks"] == ("t1",)
