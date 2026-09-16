import numpy as np
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


def test_final_probability_is_the_calibrated_ensemble_not_an_uncalibrated_average():
    frame = pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=40, freq="h", tz="UTC"),
        "target": [0, 1] * 20,
        "signal": [float(i % 7) for i in range(40)],
    })
    forecaster = LongitudinalForecaster()
    report = forecaster.fit(frame)
    assert any(score.name == "longitudinal_ensemble_isotonic" for score in report.scores)

    X = frame.iloc[-5:][["signal"]]
    probability = forecaster.predict_probability(X)
    logistic_raw = np.clip(forecaster._model.predict_proba(X)[:, 1], 1e-8, 1 - 1e-8)
    tree_raw = np.clip(forecaster._secondary.predict_proba(X)[:, 1], 1e-8, 1 - 1e-8)
    expected = forecaster._ensemble_calibrator.predict((logistic_raw + tree_raw) / 2.0)
    assert np.allclose(probability, expected)
