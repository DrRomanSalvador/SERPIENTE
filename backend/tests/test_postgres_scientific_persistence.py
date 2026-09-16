import os

import pytest

from app.scientific_discovery_engine import KnowledgeState, ScientificClaim, ScientificWork, WorkStatus
from app.scientific_work_execution import ExecutionOutcome, ScientificWorkResult
from app.postgres_storage import PostgresRuntimeStore


@pytest.mark.skipif(not os.getenv("SERPIENTE_TEST_DATABASE_URL"), reason="PostgreSQL integration environment not configured")
def test_postgres_scientific_execution_roundtrip_and_idempotency():
    store = PostgresRuntimeStore(os.environ["SERPIENTE_TEST_DATABASE_URL"])
    work = ScientificWork(
        work_id="W-PG-SCI-1",
        trigger="runtime",
        discovery="scientific execution",
        scientific_question="does the runtime object support the interpretation?",
        current_knowledge="runtime contract",
        uncertainty="observation process",
        alternative_explanations=("phenomenon", "measurement process"),
        affected_object="runtime",
        mathematical_form="Y=g(S,O,D,R,C)+epsilon",
        assumptions=("provenance exists",),
        identifiability="partial",
        data_required=("runtime",),
        temporal_requirements=("preserve timestamps",),
        falsification=("alternative explanation survives",),
        benchmark=("runtime contract",),
        validation=("structural check",),
        decision_relevance=1.0,
        expected_information_gain=1.0,
        cost=1.0,
        dependencies=(),
        owner="ESPIA",
        status=WorkStatus.SPECIFIED,
        provenance=("test",),
        stopping_rule="stop after structural check",
        capability_not_authorized=("causal effect",),
    )
    result = ScientificWorkResult("W-PG-SCI-1", "R-PG-1", ExecutionOutcome.INCONCLUSIVE, "inconclusive", ("evidence",), "OBSERVATION", True, ("causal effect",), ("test",))
    claim = ScientificClaim("C-PG-1", "runtime object exists", KnowledgeState.OBSERVATION, ("evidence",), ("test",), ("test",), ("descriptive",), ("causal effect",))
    try:
        with store.transaction():
            store.scientific_work(work)
            store.scientific_work(work)
            store.scientific_result(result)
            store.scientific_result(result)
            store.scientific_claim(claim)
            store.scientific_claim(claim)
        snapshot = store.snapshot()
        assert snapshot["scientific_work"] >= 1
        assert snapshot["scientific_results"] >= 1
        assert snapshot["scientific_claims"] >= 1
    finally:
        store.close()
