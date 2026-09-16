from datetime import datetime, timezone

import pandas as pd
import pytest

from app.pit_binding import FeatureBinding, point_in_time_fingerprint, verify_point_in_time_binding


def test_feature_matrix_fingerprint_binds_point_in_time_manifest():
    origin = datetime(2026, 1, 10, tzinfo=timezone.utc)
    frame = pd.DataFrame({"x": [3.5], "y": [7.0]})
    bindings = (
        FeatureBinding("x", ("obs-x-1",), datetime(2026, 1, 9, tzinfo=timezone.utc), ("src-v1",)),
        FeatureBinding("y", ("obs-y-1",), datetime(2026, 1, 8, tzinfo=timezone.utc), ("src-v2",), ("rolling_mean:v1",)),
    )
    fingerprint = point_in_time_fingerprint(frame, bindings, origin_time=origin)
    verify_point_in_time_binding(frame, bindings, origin_time=origin, expected_fingerprint=fingerprint)


def test_future_feature_availability_is_rejected():
    origin = datetime(2026, 1, 10, tzinfo=timezone.utc)
    frame = pd.DataFrame({"x": [3.5]})
    bindings = (FeatureBinding("x", ("obs-x-1",), datetime(2026, 1, 11, tzinfo=timezone.utc), ("src-v1",)),)
    with pytest.raises(ValueError, match="not available"):
        point_in_time_fingerprint(frame, bindings, origin_time=origin)


def test_tampered_feature_value_is_rejected():
    origin = datetime(2026, 1, 10, tzinfo=timezone.utc)
    frame = pd.DataFrame({"x": [3.5]})
    tampered = pd.DataFrame({"x": [4.5]})
    bindings = (FeatureBinding("x", ("obs-x-1",), datetime(2026, 1, 9, tzinfo=timezone.utc), ("src-v1",)),)
    fingerprint = point_in_time_fingerprint(frame, bindings, origin_time=origin)
    with pytest.raises(ValueError, match="does not bind"):
        verify_point_in_time_binding(tampered, bindings, origin_time=origin, expected_fingerprint=fingerprint)


def test_outcome_derived_feature_is_rejected():
    origin = datetime(2026, 1, 10, tzinfo=timezone.utc)
    frame = pd.DataFrame({"x": [3.5]})
    bindings = (FeatureBinding("x", ("outcome-1",), datetime(2026, 1, 9, tzinfo=timezone.utc), ("src-v1",), derived_from_outcome=True),)
    with pytest.raises(ValueError, match="not eligible"):
        point_in_time_fingerprint(frame, bindings, origin_time=origin)


def test_future_derived_feature_is_rejected():
    origin = datetime(2026, 1, 10, tzinfo=timezone.utc)
    frame = pd.DataFrame({"x": [3.5]})
    bindings = (FeatureBinding("x", ("obs-x-1",), datetime(2026, 1, 9, tzinfo=timezone.utc), ("src-v1",), future_derived=True),)
    with pytest.raises(ValueError, match="not eligible"):
        point_in_time_fingerprint(frame, bindings, origin_time=origin)
