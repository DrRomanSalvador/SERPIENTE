from datetime import datetime, timezone

from app.contracts import Observation
from app.runtime_scientific_bridge import quantitative_audit_from_runtime


def test_runtime_observation_preserves_declared_denominator_identity():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation("source", "dataset", "cases", "observed cases", "count", "Ceuta", now, now, now, "v1", 0, 10.0, ("source:v1",), "population:resident-2026")
    audit = quantitative_audit_from_runtime(observation)
    assert "denominator:population:resident-2026" in audit.predictor_definitions


def test_runtime_observation_marks_missing_denominator_explicitly():
    now = datetime(2026, 9, 16, 10, 0, tzinfo=timezone.utc)
    observation = Observation("source", "dataset", "cases", "observed cases", "count", "Ceuta", now, now, now, "v1", 0, 10.0, ("source:v1",))
    audit = quantitative_audit_from_runtime(observation)
    assert "denominator:REQUIRED" in audit.predictor_definitions
