from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import csv
import io
import json
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceHealth:
    source_id: str
    dataset_id: str
    observed_at: datetime
    status: str
    source_version: str
    content_fingerprint: str
    schema_fingerprint: str
    revision_changed: bool
    schema_changed: bool
    error: str | None = None

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.status not in {"OK", "FAILED", "BLOCKED_SCHEMA"}:
            raise ValueError("unsupported source health status")
        if not self.source_id or not self.dataset_id:
            raise ValueError("source and dataset identity are required")
        if len(self.content_fingerprint) != 64 or len(self.schema_fingerprint) != 64:
            raise ValueError("source fingerprints must be SHA-256 digests")
        if self.status in {"FAILED", "BLOCKED_SCHEMA"} and not self.error:
            raise ValueError("failed or blocked source health requires an error")


def _shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _shape(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        shapes = {_json_shape(item) for item in value[:32]}
        return {"list": sorted(shapes)}
    return type(value).__name__


def _json_shape(value: Any) -> str:
    return json.dumps(_shape(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def schema_fingerprint(payload: bytes | str) -> str:
    raw = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        reader = csv.reader(io.StringIO(raw))
        header = next(reader, [])
        shape: Any = {"format": "csv", "columns": [str(item) for item in header]}
    else:
        shape = {"format": "json", "shape": _shape(parsed)}
    canonical = json.dumps(shape, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


class SourceHealthMonitor:
    """Tracks source-process integrity separately from observation validity."""

    def __init__(self) -> None:
        self._last: dict[tuple[str, str], SourceHealth] = {}

    def record_success(self, payload: bytes | str, *, source_id: str, dataset_id: str, source_version: str, observed_at: datetime | None = None) -> SourceHealth:
        observed_at = observed_at or datetime.now(timezone.utc)
        current_schema = schema_fingerprint(payload)
        current_content = sha256(payload if isinstance(payload, bytes) else payload.encode("utf-8")).hexdigest()
        key = (source_id, dataset_id)
        previous = self._last.get(key)
        health = SourceHealth(
            source_id=source_id,
            dataset_id=dataset_id,
            observed_at=observed_at,
            status="OK",
            source_version=source_version,
            content_fingerprint=current_content,
            schema_fingerprint=current_schema,
            revision_changed=previous is not None and previous.source_version != source_version,
            schema_changed=previous is not None and previous.schema_fingerprint != current_schema,
        )
        self._last[key] = health
        return health

    def record_blocked_schema(self, health: SourceHealth, *, error: str) -> SourceHealth:
        blocked = SourceHealth(
            source_id=health.source_id,
            dataset_id=health.dataset_id,
            observed_at=health.observed_at,
            status="BLOCKED_SCHEMA",
            source_version=health.source_version,
            content_fingerprint=health.content_fingerprint,
            schema_fingerprint=health.schema_fingerprint,
            revision_changed=health.revision_changed,
            schema_changed=True,
            error=error[:1000],
        )
        self._last[(health.source_id, health.dataset_id)] = blocked
        return blocked

    def record_failure(self, *, source_id: str, dataset_id: str, error: str, observed_at: datetime | None = None) -> SourceHealth:
        observed_at = observed_at or datetime.now(timezone.utc)
        previous = self._last.get((source_id, dataset_id))
        health = SourceHealth(
            source_id=source_id,
            dataset_id=dataset_id,
            observed_at=observed_at,
            status="FAILED",
            source_version=previous.source_version if previous else "unknown",
            content_fingerprint=previous.content_fingerprint if previous else sha256(b"").hexdigest(),
            schema_fingerprint=previous.schema_fingerprint if previous else sha256(b"").hexdigest(),
            revision_changed=False,
            schema_changed=previous.schema_changed if previous else False,
            error=error[:1000],
        )
        self._last[(source_id, dataset_id)] = health
        return health

    def latest(self, source_id: str, dataset_id: str) -> SourceHealth | None:
        return self._last.get((source_id, dataset_id))


__all__ = ["SourceHealth", "SourceHealthMonitor", "schema_fingerprint"]
