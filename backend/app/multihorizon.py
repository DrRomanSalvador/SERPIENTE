from __future__ import annotations

from datetime import datetime

import pandas as pd

from .contracts import Forecast
from .pit_binding import FeatureBinding
from .prediction import LongitudinalForecaster, ValidationReport


class MultiHorizonForecaster:
    def __init__(self, horizons: tuple[str, ...]) -> None:
        if not horizons or len(set(horizons)) != len(horizons):
            raise ValueError("horizons must be non-empty and unique")
        self.horizons = horizons
        self.models = {horizon: LongitudinalForecaster(random_state=17 + i) for i, horizon in enumerate(horizons)}

    def fit(self, frames: dict[str, pd.DataFrame]) -> dict[str, ValidationReport]:
        if set(frames) != set(self.horizons):
            raise ValueError("a separate temporally ordered training frame is required for every horizon")
        return {horizon: self.models[horizon].fit(frames[horizon]) for horizon in self.horizons}

    def forecast(
        self,
        features: dict[str, pd.DataFrame],
        *,
        feature_bindings: dict[str, tuple[FeatureBinding, ...]],
        origin_time: datetime,
        target: str,
        regime: str,
        provenance: tuple[str, ...],
        point_in_time_fingerprint: str,
    ) -> tuple[Forecast, ...]:
        if set(features) != set(self.horizons) or set(feature_bindings) != set(self.horizons):
            raise ValueError("features and point-in-time bindings are required for every configured horizon")
        return tuple(
            self.models[horizon].forecast(
                features[horizon],
                feature_bindings=feature_bindings[horizon],
                origin_time=origin_time,
                target=target,
                horizon=horizon,
                regime=regime,
                provenance=provenance,
                point_in_time_fingerprint=point_in_time_fingerprint,
            )
            for horizon in self.horizons
        )
