from datetime import datetime, timezone

import pytest

from app.contracts import Observation
from app.runtime import SerpienteRuntime
from app.storage import RuntimeStore


def row(i: int) -> Observation:
    t = datetime(2026, 1, 1 + i, tzinfo=timezone.utc)
    return Observation("s", "d", f"v{i}", "semantic", "unit", "Ceuta", t, t, t, "v1", 0, 1.0, ("official",))


def test_batch_ingestion_is_atomic(tmp_path, monkeypatch):
    store = RuntimeStore(tmp_path / "atomic.sqlite")
    runtime = SerpienteRuntime(store=store)
    original = store.observation
    calls = {"n": 0}

    def fail_on_second(item):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("simulated persistence failure")
        original(item)

    monkeypatch.setattr(store, "observation", fail_on_second)
    with pytest.raises(RuntimeError):
        runtime.ingest([row(0), row(1)])
    assert store.snapshot()["observations"] == 0
    assert runtime.observations.history_at(datetime(2026, 1, 3, tzinfo=timezone.utc)) == []
    store.close()
