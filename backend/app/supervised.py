from __future__ import annotations

import pandas as pd

from .longitudinal import LongitudinalStateBuilder, PointInTimeStore


class LongitudinalSupervisedFrameBuilder:
    """Build binary future-outcome datasets directly from point-in-time history."""

    def __init__(self, *, state_builder: LongitudinalStateBuilder | None = None) -> None:
        self.state_builder = state_builder or LongitudinalStateBuilder()

    def build(self, observations, *, target_variable: str, horizon_steps: int = 1) -> pd.DataFrame:
        observations = list(observations)
        if horizon_steps < 1 or not target_variable or not observations:
            raise ValueError("observations, target_variable and positive horizon_steps are required")
        store = PointInTimeStore(); store.add(observations)
        history = store.history_at(max(row.event_time for row in observations))
        target_rows = sorted((row for row in history if row.variable_id == target_variable and not row.missing), key=lambda row: row.event_time)
        origins = sorted({row.event_time for row in history})
        rows: list[dict[str, float | object]] = []
        for origin in origins:
            future_targets = [row for row in target_rows if row.event_time > origin]
            if len(future_targets) < horizon_steps:
                continue
            visible = store.history_at(origin)
            if not visible:
                continue
            state = self.state_builder.build(visible, as_of=origin)
            if any(len(state.lags[variable]) < len(self.state_builder.lags) for variable in state.values):
                continue
            features: dict[str, float | object] = {"time": origin, "target": float(future_targets[horizon_steps - 1].value), "target_time": future_targets[horizon_steps - 1].event_time}
            for variable, value in state.values.items():
                features[f"value__{variable}"] = value
                features[f"trend__{variable}"] = state.trends[variable]
                features[f"acceleration__{variable}"] = state.accelerations[variable]
                features[f"volatility__{variable}"] = state.volatility[variable]
                for lag_index, lag_value in enumerate(state.lags[variable], start=1):
                    features[f"lag{lag_index}__{variable}"] = lag_value
            for name, value in state.interactions.items():
                features[f"interaction__{name}"] = value
            rows.append(features)
        if not rows:
            raise ValueError("insufficient longitudinal history for the requested target, horizon and lag structure")
        frame = pd.DataFrame(rows).sort_values("time").reset_index(drop=True)
        if not set(frame["target"].unique()).issubset({0.0, 1.0}):
            raise ValueError("binary longitudinal target must contain only 0/1 outcomes")
        if frame.drop(columns=["time", "target_time", "target"]).isna().any().any():
            raise ValueError("longitudinal training frame contains missing predictor values")
        return frame
