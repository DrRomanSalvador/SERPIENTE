from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss


@dataclass(frozen=True, slots=True)
class AdversarialFinding:
    name: str
    passed: bool
    reason: str


def temporal_leakage_check(frame: pd.DataFrame, *, target_time: str = "target_time") -> AdversarialFinding:
    if "time" not in frame or target_time not in frame:
        return AdversarialFinding("temporal_order", False, "time and target_time are required")
    leaked = (pd.to_datetime(frame["time"]) >= pd.to_datetime(frame[target_time])).any()
    return AdversarialFinding("future_information", not bool(leaked), "predictor time must precede target time")


def revision_leakage_check(rows: Iterable[dict], *, as_of) -> AdversarialFinding:
    for row in rows:
        if row["acquisition_time"] > as_of or row["publication_time"] > as_of:
            return AdversarialFinding("revision_leakage", False, "observation was acquired/published after forecast origin")
    return AdversarialFinding("revision_leakage", True, "all observations were point-in-time available")


def numerical_adversarial_check(values: Iterable[float]) -> AdversarialFinding:
    vals = list(values)
    return AdversarialFinding("finite_numeric", bool(vals) and all(math.isfinite(x) for x in vals), "NaN/∞ must never enter a forecast")


def calibration_report(y_true: Iterable[int], probabilities: Iterable[float]) -> dict[str, float]:
    y = np.asarray(list(y_true), dtype=int)
    p = np.asarray(list(probabilities), dtype=float)
    if len(y) != len(p) or len(y) == 0:
        raise ValueError("calibration arrays must have equal non-zero length")
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("probabilities must be finite and in [0,1]")
    return {"brier": float(brier_score_loss(y, p)), "logloss": float(log_loss(y, p, labels=[0, 1])), "mean_probability": float(p.mean()), "event_rate": float(y.mean())}


def multidomain_incremental_value(baselines: dict[str, dict[str, float]]) -> dict[str, object]:
    required = {"naive", "single_domain", "multidomain"}
    if not required.issubset(baselines):
        raise ValueError(f"missing baselines: {required - set(baselines)}")
    metric = "brier"
    naive = baselines["naive"][metric]
    multi = baselines["multidomain"][metric]
    return {"improves_brier": multi < naive, "delta_brier": naive - multi, "comparison": baselines}
