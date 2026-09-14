from __future__ import annotations

import csv
import io
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import httpx

from .contracts import Observation


class IngestionError(ValueError):
    pass


class SourceAdapter(ABC):
    @abstractmethod
    def ingest(self, payload: bytes | str, *, metadata: dict[str, Any]) -> list[Observation]:
        raise NotImplementedError


class JSONObservationAdapter(SourceAdapter):
    def ingest(self, payload: bytes | str, *, metadata: dict[str, Any]) -> list[Observation]:
        raw = json.loads(payload)
        rows = raw if isinstance(raw, list) else raw.get("observations", [])
        if not isinstance(rows, list):
            raise IngestionError("JSON observation payload must contain a list")
        return [Observation(**{**row, **metadata}) for row in rows]


class CSVObservationAdapter(SourceAdapter):
    def ingest(self, payload: bytes | str, *, metadata: dict[str, Any]) -> list[Observation]:
        reader = csv.DictReader(io.StringIO(payload.decode() if isinstance(payload, bytes) else payload))
        result = []
        for row in reader:
            row["value"] = float(row["value"])
            row["revision"] = int(row.get("revision", metadata.get("revision", 0)))
            for key in ("event_time", "publication_time", "acquisition_time"):
                row[key] = datetime.fromisoformat(row[key])
            row["provenance"] = tuple(filter(None, row.get("provenance", metadata.get("provenance", "")).split("|")))
            row.update({k: v for k, v in metadata.items() if k not in row})
            result.append(Observation(**row))
        return result


class HTTPSourceClient:
    def __init__(self, *, timeout: float = 15.0, max_bytes: int = 5_000_000) -> None:
        if timeout <= 0 or max_bytes <= 0:
            raise ValueError("timeout and max_bytes must be positive")
        self.timeout = timeout
        self.max_bytes = max_bytes

    def fetch(self, url: str, *, source_id: str, dataset_id: str) -> tuple[bytes, dict[str, Any]]:
        if not url.startswith("https://"):
            raise IngestionError("only HTTPS sources are permitted")
        with httpx.Client(timeout=self.timeout, follow_redirects=False) as client:
            response = client.get(url, headers={"Accept": "application/json,text/csv"})
            response.raise_for_status()
            if len(response.content) > self.max_bytes:
                raise IngestionError("source response exceeds configured size limit")
            publication = response.headers.get("Last-Modified")
            now = datetime.now(timezone.utc)
            return response.content, {
                "source_id": source_id,
                "dataset_id": dataset_id,
                "source_version": response.headers.get("ETag", "unknown"),
                "revision": 0,
                "acquisition_time": now,
                "publication_time": now if not publication else now,
                "provenance": (url,),
            }
