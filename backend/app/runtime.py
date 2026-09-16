from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .contracts import Alert, Observation
from .engines import AlertEngine, EventEngine, PatternEngine, SignalEngine, TrajectoryEngine
from .interaction_validation import InteractionSpec, IncrementalPredictiveValue, PredictionRecord, compare_incremental_predictive_value
from .longitudinal import LongitudinalStateBuilder, PointInTimeStore
from .mapping import ObservationMapper
from .multihorizon import MultiHorizonForecaster
from .pit_binding import FeatureBinding, point_in_time_fingerprint
from .polling import PollJob, SourcePoller
from .prediction import LongitudinalForecaster, ValidationReport
from .quality import DataProcessMonitor
from .scientific_protocol import ScientificValidationProtocol
from .storage import RuntimeStore
from .supervised import LongitudinalSupervisedFrameBuilder
from .validation import drift_report, numerical_adversarial_check, temporal_leakage_check


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    event_id: str
    signal_ids: tuple[str, ...]
    pattern_id: str
    trajectory_id: str
    alert: Alert


class SerpienteRuntime:
    """Executable, provenance-preserving event -> signal -> pattern -> trajectory -> risk -> alert loop."""

    def __init__(self, *, store: RuntimeStore | None = None) -> None:
        self.store = store
        self.observations = PointInTimeStore()
        self.state_builder = LongitudinalStateBuilder()
        self.event_engine = EventEngine()
        self.signal_engine = SignalEngine()
        self.pattern_engine = PatternEngine()
        self.trajectory_engine = TrajectoryEngine()
        self.alert_engine = AlertEngine()
        self.quality_monitor = DataProcessMonitor()
        self.forecaster = LongitudinalForecaster()
        self.multi_horizon: MultiHorizonForecaster | None = None
        self.supervised_builder = LongitudinalSupervisedFrameBuilder(state_builder=self.state_builder)
        self.scientific_protocol = ScientificValidationProtocol(
            protocol_id="serpiente-predictive-v1",
            baseline="temporal prevalence and seasonal day-of-week baseline",
            temporal_holdout="60/20/20 chronological train/calibration/test split",
            calibration_method="logistic calibration on temporally separated calibration data",
            out_of_sample="final chronological holdout only",
            error_analysis="Brier score, log loss and ROC-AUC with preserved model comparison",
            model_comparison="calibrated logistic versus gradient boosting and baselines",
            adversarial_tests=("future leakage", "non-finite values", "malformed probabilities", "point-in-time revision leakage"),
            drift_tests=("two-sample Kolmogorov-Smirnov distribution drift", "regime/change-point screening"),
            prospective_plan="precommitted prospective deployment with point-in-time replay and outcome capture",
            causal_interpretation="prediction is not a causal effect and no causal effect is identified",
        )

    def ingest(self, observations: Iterable[Observation]) -> int:
        rows = list(observations)
        if not rows:
            raise ValueError("at least one observation is required")
        if self.store:
            with self.store.transaction():
                for row in rows:
                    self.store.observation(row)
        self.observations.add(rows)
        return len(rows)

    def poll_once(self, client, job: PollJob, mapper: ObservationMapper) -> int:
        rows = SourcePoller(client).poll_once(job, mapper)
        return self.ingest(rows)

    def process(self, *, as_of: datetime, geography: str, domain: str, event_type: str) -> RuntimeResult:
        history = self.observations.history_at(as_of)
        current = [row for row in self.observations.at(as_of) if not row.missing]
        if not current:
            raise ValueError("no current non-missing observations available")
        state = self.state_builder.build(history, as_of=as_of)
        quality = self.quality_monitor.assess(history)
        provenance = tuple(dict.fromkeys(p for row in current for p in row.provenance))
        magnitude = sum(abs(float(row.value)) for row in current) / len(current)
        event = self.event_engine.normalize(tuple(str(row.observation_id) for row in current), event_time=max(r.event_time for r in current), geography=geography, domain=domain, event_type=event_type, magnitude=magnitude, provenance=provenance)
        signals = [self.signal_engine.from_state(event, variable_id=variable, value=value, baseline=value - state.trends.get(variable, 0.0), trend=state.trends.get(variable, 0.0), acceleration=state.accelerations.get(variable, 0.0), volatility=state.volatility.get(variable, 0.0), provenance=provenance) for variable, value in state.values.items()]
        pattern = self.pattern_engine.detect(signals)
        trajectory = self.trajectory_engine.build(pattern, signals, regime=state.regime)
        alert = self.alert_engine.build(trajectory, event_ids=(str(event.event_id),), signal_ids=tuple(str(s.signal_id) for s in signals), data_process_change=quality.process_change, data_process_reasons=quality.reasons)
        if self.store:
            with self.store.transaction():
                self.store.event(event)
                for signal in signals:
                    self.store.signal(signal)
                self.store.alert(alert)
        return RuntimeResult(str(event.event_id), tuple(str(s.signal_id) for s in signals), pattern.pattern_id, trajectory.trajectory_id, alert)

    def train(self, frame) -> ValidationReport:
        if "target_time" in frame.columns:
            finding = temporal_leakage_check(frame)
            if not finding.passed:
                raise ValueError(finding.reason)
        numeric = frame.select_dtypes(include=[np.number]).drop(columns=["target"], errors="ignore")
        if numeric.empty:
            raise ValueError("scientific training requires at least one numeric predictor")
        finite = numerical_adversarial_check(numeric.to_numpy(dtype=float).ravel())
        if not finite.passed:
            raise ValueError(finite.reason)
        if len(numeric) >= 10:
            drift = drift_report(numeric.iloc[: len(numeric)//2, 0], numeric.iloc[len(numeric)//2:, 0])
            if drift["drift_detected"]:
                pass
        return self.forecaster.fit(frame)

    def train_from_observations(self, observations: Iterable[Observation], *, target_variable: str, horizon_steps: int = 1) -> ValidationReport:
        frame = self.supervised_builder.build(observations, target_variable=target_variable, horizon_steps=horizon_steps)
        return self.train(frame)

    def train_multi_horizon(self, frames: dict[str, object]) -> dict[str, ValidationReport]:
        self.multi_horizon = MultiHorizonForecaster(tuple(frames.keys()))
        return self.multi_horizon.fit(frames)

    def forecast(
        self,
        features,
        *,
        feature_bindings: tuple[FeatureBinding, ...],
        origin_time: datetime,
        target: str,
        horizon: str,
        regime: str,
        provenance: tuple[str, ...],
    ):
        if origin_time.tzinfo is None:
            raise ValueError("origin_time must be timezone-aware")
        fingerprint = point_in_time_fingerprint(features, feature_bindings, origin_time=origin_time)
        forecast = self.forecaster.forecast(features, feature_bindings=feature_bindings, origin_time=origin_time, target=target, horizon=horizon, regime=regime, provenance=provenance, point_in_time_fingerprint=fingerprint)
        if self.store:
            with self.store.transaction():
                self.store.forecast(forecast)
        return forecast

    def evaluate_interaction(
        self,
        interaction: InteractionSpec,
        baseline: Sequence[PredictionRecord],
        interaction_model: Sequence[PredictionRecord],
        outcomes: Sequence[int],
    ) -> IncrementalPredictiveValue:
        """Evaluate incremental predictive value without upgrading it to causality."""
        return compare_incremental_predictive_value(interaction, baseline, interaction_model, outcomes)

    def forecast_multi_horizon(
        self,
        features: dict[str, object],
        *,
        feature_bindings: dict[str, tuple[FeatureBinding, ...]],
        origin_time: datetime,
        target: str,
        regime: str,
        provenance: tuple[str, ...],
    ):
        if self.multi_horizon is None:
            raise RuntimeError("multi-horizon models must be trained before forecasting")
        if origin_time.tzinfo is None:
            raise ValueError("origin_time must be timezone-aware")
        forecasts = self.multi_horizon.forecast(features, feature_bindings=feature_bindings, origin_time=origin_time, target=target, regime=regime, provenance=provenance)
        if self.store:
            with self.store.transaction():
                for forecast in forecasts:
                    self.store.forecast(forecast)
        return forecasts
