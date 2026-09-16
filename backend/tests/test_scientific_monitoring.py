from app.scientific_monitoring import DriftStatus, detect_cusum_change, interaction_drift


def test_cusum_detects_synthetic_regime_shift() -> None:
    result = detect_cusum_change([0.0] * 10 + [4.0] * 10, threshold=3.0)
    assert result.status == DriftStatus.DRIFT_DETECTED
    assert result.index is not None


def test_cusum_preserves_stable_series() -> None:
    result = detect_cusum_change([1.0] * 20)
    assert result.status == DriftStatus.STABLE
    assert result.index is None


def test_interaction_drift_requires_declared_metric() -> None:
    result = interaction_drift([0.1, 0.2, 0.1, 0.2], [1.1, 1.2, 1.0, 1.3], threshold=2.0, unit="declared_interaction_metric")
    assert result.status == DriftStatus.DRIFT_DETECTED
    assert result.unit == "declared_interaction_metric"
    assert "not causal" in result.interpretation
