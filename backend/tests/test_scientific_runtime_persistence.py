from datetime import datetime, timezone

from app.contracts import Observation
from app.runtime import SerpienteRuntime
from app.storage import RuntimeStore


def test_ingestion_persists_scientific_work_results_and_claim(tmp_path):
    store = RuntimeStore(tmp_path / "serpiente.sqlite")
    runtime = SerpienteRuntime(store=store)
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation(
        source_id="source-1",
        dataset_id="dataset-1",
        variable_id="hospital_demand",
        semantic_definition="daily admissions",
        unit="count/day",
        geography="Ceuta",
        event_time=now,
        publication_time=now,
        acquisition_time=now,
        source_version="v1",
        revision=0,
        value=12.0,
        provenance=("source-1:v1",),
    )
    assert runtime.ingest([observation]) == 1
    snapshot = store.snapshot()
    assert snapshot["observations"] == 1
    assert snapshot["scientific_work"] == 5
    assert snapshot["scientific_results"] == 5
    assert snapshot["scientific_claims"] == 1
    store.close()
