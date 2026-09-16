from datetime import datetime, timezone

from app.contracts import Observation
from app.runtime_scientific_bridge import work_from_runtime_object


def observation(denominator):
    now = datetime(2026, 9, 16, tzinfo=timezone.utc)
    return Observation("source", "dataset", "cases", "observed cases", "count", "Ceuta", now, now, now, "v1", 0, 10.0, ("source:v1",), denominator_id=denominator)


def test_material_denominator_change_versions_scientific_work():
    first = work_from_runtime_object(observation(None))
    second = work_from_runtime_object(observation("population:2026"))
    assert len(first) == len(second) == 5
    assert {item.work_id for item in first}.isdisjoint({item.work_id for item in second})
