from datetime import datetime, timezone

import pytest

from app.source_health import SourceHealthMonitor, schema_fingerprint


def test_schema_fingerprint_is_stable_for_key_order():
    assert schema_fingerprint('{"a": 1, "b": "x"}') == schema_fingerprint('{"b": "x", "a": 2}')


def test_monitor_detects_publisher_revision_and_schema_change():
    monitor = SourceHealthMonitor()
    first = monitor.record_success(
        '{"observations": [{"value": 1.0, "event_time": "2026-09-16T08:00:00+00:00"}]}',
        source_id="source",
        dataset_id="dataset",
        source_version="v1",
        observed_at=datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc),
    )
    assert first.status == "OK"
    second = monitor.record_success(
        '{"observations": [{"value": 1.0, "event_time": "2026-09-16T08:00:00+00:00", "quality": 1.0}]}',
        source_id="source",
        dataset_id="dataset",
        source_version="v2",
        observed_at=datetime(2026, 9, 16, 8, 1, tzinfo=timezone.utc),
    )
    assert second.revision_changed
    assert second.schema_changed


def test_blocked_schema_is_explicit_and_preserved():
    monitor = SourceHealthMonitor()
    first = monitor.record_success(
        '{"observations": [{"value": 1.0}]}',
        source_id="source",
        dataset_id="dataset",
        source_version="v1",
    )
    second = monitor.record_success(
        '{"observations": [{"value": 1.0, "unexpected": true}]}',
        source_id="source",
        dataset_id="dataset",
        source_version="v1",
    )
    blocked = monitor.record_blocked_schema(second, error="mapper contract changed")
    assert first.status == "OK"
    assert blocked.status == "BLOCKED_SCHEMA"
    assert blocked.schema_changed
    assert blocked.error == "mapper contract changed"
    assert monitor.latest("source", "dataset") == blocked


def test_invalid_health_status_fails_closed():
    monitor = SourceHealthMonitor()
    with pytest.raises(ValueError):
        monitor.record_failure(source_id="source", dataset_id="dataset", error="timeout")
    # A failed first observation is still represented with explicit unknown fingerprints.
    health = monitor.record_failure(source_id="source", dataset_id="dataset", error="timeout")
    assert health.status == "FAILED"
