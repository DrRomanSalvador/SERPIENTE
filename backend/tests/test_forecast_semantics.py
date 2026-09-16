from datetime import datetime, timezone

import pytest

from app.contracts import Forecast


def _forecast(**overrides):
    base = dict(
        forecast_id="f1",
        origin_time=datetime(2026, 9, 16, 12, tzinfo=timezone.utc),
        horizon="P1D",
        target="event",
        probability=0.5,
        lower=0.2,
        upper=0.8,
        aleatoric=0.1,
        epistemic=0.1,
        measurement=0.0,
        parameter=0.1,
        structural=0.1,
        model_disagreement=0.05,
        regime="BASELINE",
        provenance=("source",),
        point_in_time_fingerprint="fingerprint",
    )
    base.update(overrides)
    return Forecast(**base)


def test_forecast_interval_is_explicitly_uncalibrated_by_default() -> None:
    forecast = _forecast()
    assert forecast.interval_semantics == "HEURISTIC_UNCALIBRATED"


def test_unknown_interval_semantics_are_rejected() -> None:
    with pytest.raises(ValueError, match="interval semantics"):
        _forecast(interval_semantics="CALIBRATED")
