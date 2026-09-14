import numpy as np

from app.validation import drift_report


def test_drift_detection_is_statistical_and_explicit():
    rng = np.random.default_rng(17)
    report = drift_report(rng.normal(0, 1, 100), rng.normal(4, 1, 100))
    assert report["drift_detected"] is True
    assert report["p_value"] < report["alpha"]
