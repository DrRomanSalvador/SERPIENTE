from datetime import datetime, timedelta, timezone

from app.contracts import Observation
from app.runtime import SerpienteRuntime
from app.storage import RuntimeStore


def observation(event_time, value):
    return Observation("source", "dataset", "cases", "observed cases", "count", "Ceuta", event_time, event_time, event_time, "v1", 0, value, ("source:v1",))


def test_recurring_observations_do_not_create_duplicate_semantic_work(tmp_path):
    store = RuntimeStore(tmp_path / "runtime.sqlite")
    runtime = SerpienteRuntime(store=store)
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    runtime.ingest([observation(t0, 10.0)])
    runtime.ingest([observation(t0 + timedelta(days=1), 12.0)])
    snapshot = store.snapshot()
    assert snapshot["scientific_work"] == 5
    assert snapshot["scientific_results"] == 10
    assert snapshot["scientific_claims"] == 2
    store.close()
