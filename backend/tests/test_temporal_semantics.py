from datetime import datetime, timedelta, timezone

import pytest

from app.contracts import Observation


def _observation(**overrides):
    base = dict(
        source_id="source",
        dataset_id="dataset",
        variable_id="variable",
        semantic_definition="test",
        unit="count",
        geography="Ceuta",
        event_time=datetime(2026, 9, 16, 8, tzinfo=timezone.utc),
        publication_time=datetime(2026, 9, 16, 9, tzinfo=timezone.utc),
        acquisition_time=datetime(2026, 9, 16, 10, tzinfo=timezone.utc),
        source_version="v1",
        revision=1,
        value=1.0,
        provenance=("source",),
    )
    base.update(overrides)
    return Observation(**base)


def test_knowledge_time_controls_point_in_time_eligibility() -> None:
    observation = _observation(knowledge_time=datetime(2026, 9, 16, 12, tzinfo=timezone.utc), vintage_id="v1")
    assert not observation.known_at(datetime(2026, 9, 16, 11, tzinfo=timezone.utc))
    assert observation.known_at(datetime(2026, 9, 16, 12, tzinfo=timezone.utc))


def test_revision_and_knowledge_order_are_enforced() -> None:
    with pytest.raises(ValueError, match="knowledge_time"):
        _observation(
            revision_time=datetime(2026, 9, 16, 12, tzinfo=timezone.utc),
            knowledge_time=datetime(2026, 9, 16, 11, tzinfo=timezone.utc),
        )


def test_processing_time_cannot_precede_acquisition() -> None:
    with pytest.raises(ValueError, match="processing_time"):
        _observation(processing_time=datetime(2026, 9, 16, 9, 30, tzinfo=timezone.utc))


def test_to_dict_preserves_vintage_and_temporal_metadata() -> None:
    observation = _observation(
        processing_time=datetime(2026, 9, 16, 10, 30, tzinfo=timezone.utc),
        revision_time=datetime(2026, 9, 16, 11, tzinfo=timezone.utc),
        knowledge_time=datetime(2026, 9, 16, 12, tzinfo=timezone.utc),
        vintage_id="v2",
    )
    data = observation.to_dict()
    assert data["vintage_id"] == "v2"
    assert data["knowledge_time"].endswith("+00:00")
