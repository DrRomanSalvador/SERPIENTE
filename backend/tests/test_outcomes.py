from datetime import datetime, timedelta, timezone

import pytest

from app.outcomes import ForecastOutcome


def test_outcome_feedback_is_linked_and_scored():
    origin = datetime(2026,1,1,tzinfo=timezone.utc)
    outcome = ForecastOutcome("p1", origin, origin + timedelta(days=1), "risk", 1, 0.8, "24h", ("official:outcome",))
    assert outcome.brier_error == pytest.approx(0.04)
    assert outcome.log_loss_error > 0


def test_outcome_cannot_precede_forecast():
    origin = datetime(2026,1,2,tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="precede"):
        ForecastOutcome("p1", origin, origin - timedelta(minutes=1), "risk", 0, 0.2, "24h", ("official",))
