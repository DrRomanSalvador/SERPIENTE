from datetime import datetime, timedelta, timezone

import pytest

from app.outcomes import ForecastOutcome


def _outcome(**overrides):
    base = dict(
        prediction_id="p1",
        origin_time=datetime(2026, 9, 16, 8, tzinfo=timezone.utc),
        outcome_time=datetime(2026, 9, 17, 8, tzinfo=timezone.utc),
        target="event",
        observed=1,
        predicted_probability=0.7,
        horizon="P1D",
        provenance=("source",),
    )
    base.update(overrides)
    return ForecastOutcome(**base)


def test_outcome_is_not_eligible_before_availability() -> None:
    available = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)
    outcome = _outcome(available_at=available, vintage_id="v1")
    assert not outcome.eligible_at(available - timedelta(seconds=1))
    assert outcome.eligible_at(available)


def test_outcome_availability_cannot_precede_outcome_time() -> None:
    with pytest.raises(ValueError, match="available_at"):
        _outcome(available_at=datetime(2026, 9, 17, 7, tzinfo=timezone.utc))
