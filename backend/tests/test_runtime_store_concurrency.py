from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from app.contracts import Observation
from app.storage import RuntimeStore


def _observation(i: int) -> Observation:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i)
    return Observation(
        "concurrency-source",
        "concurrency-dataset",
        "risk",
        "concurrency regression",
        "unit",
        "Ceuta",
        timestamp,
        timestamp,
        timestamp,
        "v1",
        0,
        float(i),
        ("official:concurrency",),
    )


def test_runtime_store_serializes_shared_connection_reads_and_writes(tmp_path):
    store = RuntimeStore(tmp_path / "concurrency.sqlite")
    observations = [_observation(i) for i in range(64)]

    def write(item: Observation) -> None:
        store.observation(item)

    def read() -> int:
        return store.snapshot()["observations"]

    try:
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(write, item) for item in observations]
            futures.extend(executor.submit(read) for _ in range(64))
            for future in futures:
                future.result()

        assert store.snapshot()["observations"] == len(observations)
    finally:
        store.close()
