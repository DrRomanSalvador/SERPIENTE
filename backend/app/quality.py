from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from statistics import median

from .contracts import Observation


@dataclass(frozen=True, slots=True)
class DataProcessAssessment:
    process_change: bool
    severity: float
    reasons: tuple[str, ...]


class DataProcessMonitor:
    def assess(self, history: list[Observation]) -> DataProcessAssessment:
        if len(history) < 6:
            return DataProcessAssessment(False, 0.0, ())
        ordered = sorted(history, key=lambda x: x.event_time)
        intervals = [(b.event_time - a.event_time).total_seconds() for a, b in zip(ordered, ordered[1:]) if b.event_time > a.event_time]
        reasons: list[str] = []
        severity = 0.0
        if len(intervals) >= 4:
            baseline = median(intervals[:-2])
            recent = median(intervals[-2:])
            if baseline > 0 and (recent > 2.5 * baseline or recent < baseline / 2.5):
                reasons.append("observation cadence changed materially")
                severity = max(severity, 0.8)
        versions = [x.source_version for x in ordered]
        if len(set(versions[-3:])) > 1:
            reasons.append("source version changed in recent observations")
            severity = max(severity, 0.6)
        missing_recent = sum(1 for x in ordered[-5:] if x.missing) / min(5, len(ordered))
        missing_previous = sum(1 for x in ordered[-10:-5] if x.missing) / max(1, min(5, len(ordered) - 5))
        if missing_recent - missing_previous >= 0.4:
            reasons.append("missingness increased materially")
            severity = max(severity, 0.8)
        return DataProcessAssessment(bool(reasons), min(1.0, severity), tuple(reasons))
