from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Sequence

import pandas as pd


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class FeatureBinding:
    feature_name: str
    observation_ids: tuple[str, ...]
    available_at: datetime
    source_versions: tuple[str, ...]
    transformation_lineage: tuple[str, ...] = ()
    derived_from_outcome: bool = False
    future_derived: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "available_at", _utc(self.available_at, "available_at"))
        if not self.feature_name or not self.observation_ids or not self.source_versions:
            raise ValueError("feature binding requires feature, observations and source versions")


def point_in_time_fingerprint(
    frame: pd.DataFrame,
    bindings: Sequence[FeatureBinding],
    *,
    origin_time: datetime,
) -> str:
    origin = _utc(origin_time, "origin_time")
    names = tuple(frame.columns)
    by_name = {item.feature_name: item for item in bindings}
    if not names or set(names) != set(by_name):
        raise ValueError("feature bindings must exactly cover forecast features")
    if frame.empty:
        raise ValueError("forecast feature frame cannot be empty")
    for name in names:
        binding = by_name[name]
        if binding.available_at > origin:
            raise ValueError(f"feature {name} was not available at forecast origin")
        if binding.derived_from_outcome or binding.future_derived:
            raise ValueError(f"feature {name} is not eligible for point-in-time forecasting")
    row = frame.iloc[-1]
    payload = {
        "origin_time": origin.isoformat(),
        "features": {
            name: {
                "value": float(row[name]),
                "observation_ids": tuple(sorted(by_name[name].observation_ids)),
                "available_at": by_name[name].available_at.isoformat(),
                "source_versions": tuple(sorted(by_name[name].source_versions)),
                "transformation_lineage": tuple(by_name[name].transformation_lineage),
                "derived_from_outcome": by_name[name].derived_from_outcome,
                "future_derived": by_name[name].future_derived,
            }
            for name in sorted(names)
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(canonical.encode()).hexdigest()


def verify_point_in_time_binding(
    frame: pd.DataFrame,
    bindings: Sequence[FeatureBinding],
    *,
    origin_time: datetime,
    expected_fingerprint: str,
) -> None:
    actual = point_in_time_fingerprint(frame, bindings, origin_time=origin_time)
    if actual != expected_fingerprint:
        raise ValueError("point-in-time fingerprint does not bind the supplied forecast feature matrix")


__all__ = ["FeatureBinding", "point_in_time_fingerprint", "verify_point_in_time_binding"]
