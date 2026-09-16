from datetime import datetime, timezone

from app.contracts import Observation


def test_observation_existing_positional_quality_argument_remains_quality():
    now = datetime(2026, 9, 16, tzinfo=timezone.utc)
    observation = Observation("s", "d", "v", "semantic", "count", "Ceuta", now, now, now, "v1", 0, 1.0, ("source",), 0.5)
    assert observation.quality == 0.5
    assert observation.denominator_id is None
