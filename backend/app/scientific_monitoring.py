"""Generic descriptive diagnostics for regime and interaction drift.

These diagnostics identify distributional/relationship changes. They do not
establish causes, mechanisms, or future harm and are not predictive validity
claims by themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite, sqrt
from statistics import mean
from typing import Sequence


class DriftStatus(StrEnum):
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True, slots=True)
class ChangePointResult:
    index: int | None
    statistic: float
    threshold: float
    status: DriftStatus


@dataclass(frozen=True, slots=True)
class InteractionDriftResult:
    reference_mean: float
    current_mean: float
    standardized_shift: float
    threshold: float
    status: DriftStatus
    unit: str
    interpretation: str


def detect_cusum_change(
    values: Sequence[float],
    *,
    reference_mean: float | None = None,
    allowance: float = 0.0,
    threshold: float = 5.0,
) -> ChangePointResult:
    """One-sided absolute CUSUM change diagnostic with deterministic output."""
    if len(values) < 3:
        return ChangePointResult(None, 0.0, threshold, DriftStatus.INSUFFICIENT_DATA)
    if not all(isfinite(value) for value in values):
        raise ValueError("values must be finite")
    if threshold <= 0 or allowance < 0:
        raise ValueError("threshold must be positive and allowance non-negative")
    center = mean(values[: max(2, len(values) // 3)]) if reference_mean is None else reference_mean
    deviations = [value - center for value in values]
    scale = sqrt(sum((value - center) ** 2 for value in deviations) / max(1, len(deviations) - 1))
    if scale <= 0:
        return ChangePointResult(None, 0.0, threshold, DriftStatus.STABLE)
    positive = 0.0
    negative = 0.0
    for index, value in enumerate(values):
        normalized = (value - center) / scale
        positive = max(0.0, positive + normalized - allowance)
        negative = min(0.0, negative + normalized + allowance)
        statistic = max(positive, -negative)
        if statistic >= threshold:
            return ChangePointResult(index, statistic, threshold, DriftStatus.DRIFT_DETECTED)
    return ChangePointResult(None, max(positive, -negative), threshold, DriftStatus.STABLE)


def interaction_drift(
    reference: Sequence[float],
    current: Sequence[float],
    *,
    threshold: float = 2.0,
    unit: str = "standardized_mean_shift",
) -> InteractionDriftResult:
    """Compare a declared interaction metric across two periods.

    The caller supplies the interaction metric; this function does not infer an
    interaction from raw co-movement and does not interpret the shift causally.
    """
    if len(reference) < 2 or len(current) < 2:
        return InteractionDriftResult(0.0, 0.0, 0.0, threshold, DriftStatus.INSUFFICIENT_DATA, unit, "Insufficient observations")
    if not all(isfinite(value) for value in (*reference, *current)):
        raise ValueError("interaction metrics must be finite")
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    reference_mean = mean(reference)
    current_mean = mean(current)
    variance = sum((value - reference_mean) ** 2 for value in reference) / max(1, len(reference) - 1)
    standard_error = sqrt(variance / len(reference) + variance / len(current))
    standardized_shift = abs(current_mean - reference_mean) / standard_error if standard_error > 0 else 0.0
    status = DriftStatus.DRIFT_DETECTED if standardized_shift >= threshold else DriftStatus.STABLE
    interpretation = (
        "Declared interaction metric changed beyond threshold; this is descriptive and not causal."
        if status == DriftStatus.DRIFT_DETECTED
        else "No threshold-crossing change in the declared interaction metric was detected."
    )
    return InteractionDriftResult(reference_mean, current_mean, standardized_shift, threshold, status, unit, interpretation)
