import numpy as np
import pandas as pd

from app.multihorizon import MultiHorizonForecaster


def frame(offset: int = 0):
    n = 50
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="D", tz="UTC"), "x": np.arange(n, dtype=float) + offset, "target": (np.arange(n) % 2).astype(int)})


def test_each_horizon_has_its_own_temporal_model():
    model = MultiHorizonForecaster(("24h", "7d"))
    reports = model.fit({"24h": frame(), "7d": frame(10)})
    assert set(reports) == {"24h", "7d"}
    forecasts = model.forecast({"24h": frame().tail(1)[["x"]], "7d": frame(10).tail(1)[["x"]]}, origin_time=pd.Timestamp("2026-02-20", tz="UTC").to_pydatetime(), target="risk", regime="STABLE", provenance=("official",), point_in_time_fingerprint="a"*64)
    assert {forecast.horizon for forecast in forecasts} == {"24h", "7d"}
