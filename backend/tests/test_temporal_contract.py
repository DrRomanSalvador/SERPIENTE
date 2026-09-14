from datetime import datetime, timedelta, timezone
import pytest
from app.contracts import Observation


def test_event_cannot_be_acquired_before_it_occurs():
    event = datetime(2026, 1, 2, tzinfo=timezone.utc)
    acquisition = event - timedelta(hours=1)
    with pytest.raises(ValueError, match="event_time"):
        Observation("s", "d", "v", "semantic", "unit", "Ceuta", event, acquisition, acquisition, "v1", 0, 1.0, ("official",))
