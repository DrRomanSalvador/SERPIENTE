from __future__ import annotations

from datetime import timedelta

import pandas as pd

from .longitudinal import LongitudinalStateBuilder, PointInTimeStore


class LongitudinalSupervisedFrameBuilder:
    """Build binary future-outcome datasets directly from the observation history.

    Each row is generated at an origin time and uses only information known at that
    origin. The target is read strictly from a later event time.
    """

    def __init__(self, *, state_builder: LongitudinalStateBuilder | None = None) -> None:
        self.state_builder = state_builder or LongitudinalStateBuilder()

    def build(self, observations, *, target_variable: str, horizon_steps: int = 1) -> pd.DataFrame:
        if horizon_steps < 1 or not target_variable:
            raise ValueError("target_variable and positive horizon_steps are required")
        store = PointInTimeStore(); store.add(observations)
        history = store.history_at(max(row.event_time for row in store._rows))
        target_rows = sorted((row for row in history if row.variable_id == target_variable and not row.missing), key=lambda row: row.event_time)
        origins = sorted({row.event_time for row in history})
        rows: list[dict[str, float | object]] = []
        for index, origin in enumerate(origins):
            future_targets = [row for row in target_rows if row.event_time > origin]
            if len(future_targets) < horizon_steps:
                continue
            target = future_targets[horizon_steps - 1]
            visible = store.history_at(origin)
            if not visible:
                continue
            state = self.state_builder.build(visible, as_of=origin)
            features: dict[str, float | object] = {"time": origin, "target": float(target.value), "target_time": target.event_time}
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
            raise ValueError("insufficient longitudinal history for the requested target and horizon")
        frame = pd.DataFrame(rows).sort_values("time").reset_index(drop=True)
        if not set(frame["target"].unique()).issubset({0.0, 1.0}):
            raise ValueError("binary longitudinal target must contain only 0/1 outcomes")
        return frame
