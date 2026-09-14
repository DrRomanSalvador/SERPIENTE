from datetime import datetime, timezone
import pytest

from app.contracts import Observation
from app.longitudinal import LongitudinalStateBuilder


def test_same_time_conflicting_sources_are_not_averaged():
    t = datetime(2026,1,1,tzinfo=timezone.utc)
    rows = [
        Observation("s1","d","v","semantic","unit","Ceuta",t,t,t,"v1",0,1.0,("official:s1",)),
        Observation("s2","d","v","semantic","unit","Ceuta",t,t,t,"v1",0,2.0,("official:s2",)),
    ]
    with pytest.raises(ValueError, match="conflicting observations"):
        LongitudinalStateBuilder().build(rows, as_of=t)
