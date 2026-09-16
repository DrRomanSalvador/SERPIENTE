from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Sequence

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .contracts import Forecast
from .pit_binding import FeatureBinding, verify_point_in_time_binding


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
    """Binary longitudinal forecaster with temporal holdout, calibration and model disagreement."""

    def __init__(self, *, random_state: int = 17) -> None:
        self.random_state = random_state
        self._model: Any = None
        self._secondary: Any = None
        self._calibrator: IsotonicRegression | None = None
        self._ensemble_calibrator: IsotonicRegression | None = None
        self._feature_names: tuple[str, ...] = ()
        self._train_rows = 0
        self._calibration_rows = 0
        self._seasonal_rates: dict[int, float] = {}

    @staticmethod
    def _check_frame(frame: pd.DataFrame) -> None:
        required = {"time", "target"}
        if not required.issubset(frame.columns):
            raise ValueError(f"missing required columns: {required - set(frame.columns)}")
        if frame["time"].isna().any() or not frame["time"].is_monotonic_increasing or frame["time"].duplicated().any():
            raise ValueError("training frame must be strictly ordered with unique forecast origins")
        if frame["target"].isna().any():
            raise ValueError("target cannot be missing")
        target_values = set(pd.unique(frame["target"]))
        if not target_values.issubset({0, 1}):
            raise ValueError("target must be binary with values in {0,1}")

    def fit(self, frame: pd.DataFrame) -> ValidationReport:
        self._check_frame(frame)
        if len(frame) < 30:
            raise ValueError("at least 30 ordered observations are required")
        feature_names = [c for c in frame.columns if c not in {"time", "target", "target_time"}]
        if not feature_names:
            raise ValueError("no predictors supplied")
        if any(not np.issubdtype(frame[c].dtype, np.number) for c in feature_names):
            raise ValueError("predictors must be numeric")
        if not np.isfinite(frame[feature_names].to_numpy(dtype=float)).all():
            raise ValueError("predictors must be finite")
        if set(frame[feature_names]).intersection({"future_target", "outcome_time", "post_outcome"}):
            raise ValueError("explicit post-outcome columns are forbidden")
        n = len(frame)
        train_end = int(n * 0.60)
        cal_end = int(n * 0.80)
        if train_end < 20 or cal_end <= train_end + 5 or n - cal_end < 5:
            raise ValueError("insufficient temporal holdout")
        X_train, y_train = frame.iloc[:train_end][feature_names], frame.iloc[:train_end]["target"].astype(int)
        X_cal, y_cal = frame.iloc[train_end:cal_end][feature_names], frame.iloc[train_end:cal_end]["target"].astype(int)
        X_test, y_test = frame.iloc[cal_end:][feature_names], frame.iloc[cal_end:]["target"].astype(int)
        if any(y.nunique() < 2 for y in (y_train, y_cal, y_test)):
            raise ValueError("each temporal split must contain both target classes")
        self._feature_names = tuple(feature_names)
        self._train_rows = len(X_train)
        self._calibration_rows = len(X_cal)
        self._model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=self.random_state))
        self._secondary = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, random_state=self.random_state)
        self._model.fit(X_train, y_train)
        self._secondary.fit(X_train, y_train)
        logistic_raw = np.clip(self._model.predict_proba(X_cal)[:, 1], 1e-8, 1 - 1e-8)
        tree_raw = np.clip(self._secondary.predict_proba(X_cal)[:, 1], 1e-8, 1 - 1e-8)
        self._calibrator = IsotonicRegression(y_min=0.0, y_max=1.0, increasing=True, out_of_bounds="clip")
        self._calibrator.fit(logistic_raw, y_cal.to_numpy())
        ensemble_raw = (logistic_raw + tree_raw) / 2.0
        self._ensemble_calibrator = IsotonicRegression(y_min=0.0, y_max=1.0, increasing=True, out_of_bounds="clip")
        self._ensemble_calibrator.fit(ensemble_raw, y_cal.to_numpy())
        cal_times = pd.to_datetime(frame.iloc[train_end:cal_end]["time"], utc=True)
        self._seasonal_rates = {int(day): float(y_cal.to_numpy()[cal_times.dt.dayofweek.to_numpy() == day].mean()) for day in range(7) if (cal_times.dt.dayofweek == day).any()}
        ensemble, tree = self._predict_pair(X_test)
        logistic = np.asarray(self._calibrator.predict(np.clip(self._model.predict_proba(X_test)[:, 1], 1e-8, 1 - 1e-8)), dtype=float)
        prevalence = np.full(len(y_test), float(y_train.mean()))
        test_times = pd.to_datetime(frame.iloc[cal_end:]["time"], utc=True)
        seasonal = np.array([self._seasonal_rates.get(int(day), float(y_train.mean())) for day in test_times.dt.dayofweek], dtype=float)
        scores = [
            ModelScore("longitudinal_logistic_isotonic", float(brier_score_loss(y_test, logistic)), float(log_loss(y_test, logistic, labels=[0, 1])), float(roc_auc_score(y_test, logistic))),
            ModelScore("longitudinal_gradient_boosting", float(brier_score_loss(y_test, tree)), float(log_loss(y_test, tree, labels=[0, 1])), float(roc_auc_score(y_test, tree))),
            ModelScore("longitudinal_ensemble_isotonic", float(brier_score_loss(y_test, ensemble)), float(log_loss(y_test, ensemble, labels=[0, 1])), float(roc_auc_score(y_test, ensemble))),
            ModelScore("temporal_prevalence_baseline", float(brier_score_loss(y_test, prevalence)), float(log_loss(y_test, prevalence, labels=[0, 1])), None),
            ModelScore("seasonal_dayofweek_baseline", float(brier_score_loss(y_test, seasonal)), float(log_loss(y_test, seasonal, labels=[0, 1])), None),
        ]
        return ValidationReport(train_end, cal_end - train_end, n - cal_end, tuple(scores), False, True)

    def _predict_pair(self, X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        if self._model is None or self._secondary is None or self._calibrator is None or self._ensemble_calibrator is None:
            raise RuntimeError("model is not fitted")
        X = X.loc[:, self._feature_names]
        logistic_raw = np.clip(self._model.predict_proba(X)[:, 1], 1e-8, 1 - 1e-8)
        tree_raw = np.clip(self._secondary.predict_proba(X)[:, 1], 1e-8, 1 - 1e-8)
        ensemble_raw = (logistic_raw + tree_raw) / 2.0
        ensemble = np.asarray(self._ensemble_calibrator.predict(ensemble_raw), dtype=float)
        if not np.isfinite(ensemble).all() or not np.isfinite(tree_raw).all():
            raise RuntimeError("non-finite forecast produced")
        return ensemble, tree_raw

    def predict_probability(self, X: pd.DataFrame) -> np.ndarray:
        ensemble, _ = self._predict_pair(X)
        return ensemble

    def forecast(
        self,
        X: pd.DataFrame,
        *,
        origin_time: datetime,
        target: str,
        horizon: str,
        regime: str,
        provenance: tuple[str, ...],
        point_in_time_fingerprint: str,
        feature_bindings: Sequence[FeatureBinding],
        model_disagreement: float = 0.0,
    ) -> Forecast:
        origin = origin_time.astimezone(timezone.utc) if origin_time.tzinfo else None
        if origin is None:
            raise ValueError("origin_time must be timezone-aware")
        verify_point_in_time_binding(X.loc[:, self._feature_names], feature_bindings, origin_time=origin, expected_fingerprint=point_in_time_fingerprint)
        ensemble, tree = self._predict_pair(X)
        disagreement = float(abs(ensemble[-1] - tree[-1]))
        if model_disagreement:
            disagreement = max(disagreement, model_disagreement)
        p = float(ensemble[-1])
        aleatoric = min(1.0, 2.0 * p * (1.0 - p))
        epistemic = min(1.0, 1.0 / np.sqrt(max(1, self._train_rows)))
        parameter = min(1.0, 1.0 / np.sqrt(max(1, self._calibration_rows)))
        structural = min(1.0, (0.6 if regime != "STABLE" else 0.0) + disagreement)
        measurement = 0.0
        total = min(1.0, 0.25 * aleatoric + epistemic + parameter + structural + disagreement)
        return Forecast(str(sha256(f"{origin.isoformat()}:{target}:{horizon}:{point_in_time_fingerprint}".encode()).hexdigest()), origin, horizon, target, p, max(0.0, p - total), min(1.0, p + total), aleatoric, epistemic, measurement, parameter, structural, disagreement, regime, provenance, point_in_time_fingerprint)
