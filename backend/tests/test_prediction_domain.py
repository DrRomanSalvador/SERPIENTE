import pandas as pd
import pytest

from app.prediction import LongitudinalForecaster


def test_forecaster_rejects_non_binary_target():
    frame = pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=30, freq="h", tz="UTC"),
        "target": [0, 1, 2] * 10,
        "signal": [float(i) for i in range(30)],
    })
    with pytest.raises(ValueError, match="binary"):
        LongitudinalForecaster().fit(frame)
