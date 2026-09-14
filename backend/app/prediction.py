from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from .contracts import Forecast


@dataclass(frozen=True, slots=True)
class ModelScore:
    name: str
    brier: float
    logloss: float
    auc: float | None


@dataclass(frozen=True, slots=True)
class ValidationReport:
    train_rows: int
    calibration_rows: int
    test_rows: int
    scores: tuple[ModelScore, ...]
    leakage_detected: bool
    temporal_order_valid: bool


class LongitudinalForecaster:
    """Binary event forecaster using only features available at the forecast origin."""

    def __init__(self, *, random_state: int = 17) -> None:
        self.random_state = random_state
        self._model: Any = None
        self._feature_names: tuple[str, ...] = ()
        self._calibration_a = 1.0
        self._calibration_b = 0.0

    @staticmethod
    def _check_frame(frame: pd.DataFrame) -> None:
        required = {"time", "target"}
        if not required.issubset(frame.columns):
            raise ValueError(f"missing required columns: {required - set(frame.columns)}")
        if frame["time"].isna().any() or not frame["time"].is_monotonic_increasing:
            raise ValueError("training frame must be strictly point-in-time ordered")
        if frame["target"].isna().any():
            raise ValueError("target cannot be missing")

    def fit(self, frame: pd.DataFrame) -> ValidationReport:
        self._check_frame(frame)
        if len(frame) < 30:
            raise ValueError("at least 30 ordered observations are required")
        feature_names = [c for c in frame.columns if c not in {"time", "target"}]
        if not feature_names:
            raise ValueError("no predictors supplied")
        if any(not np.issubdtype(frame[c].dtype, np.number) for c in feature_names):
            raise ValueError("predictors must be numeric")
        if not np.isfinite(frame[feature_names].to_numpy(dtype=float)).all():
            raise ValueError("predictors must be finite")
        if set(frame[feature_names]).intersection({"future_target", "outcome_time", "post_outcome"}):
            raise ValueError("explicit post-outcome columns are forbidden")
        n = len(frame)
        train_end = max(20, int(n * 0.60))
        cal_end = max(train_end + 5, int(n * 0.80))
        if cal_end >= n:
            raise ValueError("insufficient temporal holdout")
        X_train, y_train = frame.iloc[:train_end][feature_names], frame.iloc[:train_end]["target"].astype(int)
        X_cal, y_cal = frame.iloc[train_end:cal_end][feature_names], frame.iloc[train_end:cal_end]["target"].astype(int)
        X_test, y_test = frame.iloc[cal_end:][feature_names], frame.iloc[cal_end:]["target"].astype(int)
        if y_train.nunique() < 2 or y_cal.nunique() < 2 or y_test.nunique() < 2:
            raise ValueError("each temporal split must contain both target classes")
        self._feature_names = tuple(feature_names)
        self._model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=self.random_state))
        self._model.fit(X_train, y_train)
        cal_raw = self._model.predict_proba(X_cal)[:, 1]
        logits = np.log(np.clip(cal_raw, 1e-8, 1 - 1e-8) / np.clip(1 - cal_raw, 1e-8, 1 - 1e-8))
        design = np.column_stack([logits, np.ones_like(logits)])
        coef, *_ = np.linalg.lstsq(design, y_cal.to_numpy(), rcond=None)
        self._calibration_a, self._calibration_b = map(float, coef)
        scores: list[ModelScore] = []
        pred = self.predict_probability(X_test)
        scores.append(ModelScore("longitudinal_logistic", float(brier_score_loss(y_test, pred)), float(log_loss(y_test, pred, labels=[0, 1])), float(roc_auc_score(y_test, pred))))
        persistence = float(y_cal.mean())
        naive = np.full(len(y_test), persistence)
        scores.append(ModelScore("temporal_prevalence_baseline", float(brier_score_loss(y_test, naive)), float(log_loss(y_test, naive, labels=[0, 1])), None))
        return ValidationReport(train_end, cal_end - train_end, n - cal_end, tuple(scores), False, True)

    def predict_probability(self, X: pd.DataFrame) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("model is not fitted")
        X = X.loc[:, self._feature_names]
        raw = np.clip(self._model.predict_proba(X)[:, 1], 1e-8, 1 - 1e-8)
        logits = np.log(raw / (1 - raw))
        calibrated = 1 / (1 + np.exp(-(self._calibration_a * logits + self._calibration_b)))
        if not np.isfinite(calibrated).all():
            raise RuntimeError("non-finite forecast produced")
        return calibrated

    def forecast(self, X: pd.DataFrame, *, origin_time: datetime, target: str, horizon: str, regime: str, provenance: tuple[str, ...], point_in_time_fingerprint: str, model_disagreement: float = 0.0) -> Forecast:
        origin = origin_time.astimezone(timezone.utc) if origin_time.tzinfo else None
        if origin is None:
            raise ValueError("origin_time must be timezone-aware")
        p = float(self.predict_probability(X)[-1])
        epistemic = min(1.0, 1.0 / max(1.0, len(X)))
        structural = min(1.0, 0.5 * (1.0 if regime != "STABLE" else 0.0) + model_disagreement)
        total = min(1.0, 0.20 + epistemic + structural + model_disagreement)
        return Forecast(str(sha256(f"{origin.isoformat()}:{target}:{horizon}:{point_in_time_fingerprint}".encode()).hexdigest()), origin, horizon, target, p, max(0.0, p - total), min(1.0, p + total), 0.10, epistemic, 0.05, 0.05, structural, model_disagreement, regime, provenance, point_in_time_fingerprint)
