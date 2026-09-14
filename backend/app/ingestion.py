from __future__ import annotations

import csv
import io
import ipaddress
import json
import socket
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
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
            row["value"] = None if row.get("value", "").strip() == "" else float(row["value"])
            row["missing"] = str(row.get("missing", "false")).lower() == "true"
            row["revision"] = int(row.get("revision", metadata.get("revision", 0)))
            for key in ("event_time", "publication_time", "acquisition_time"):
                row[key] = datetime.fromisoformat(row[key])
            row["provenance"] = tuple(filter(None, row.get("provenance", metadata.get("provenance", "")).split("|")))
            row.update({k: v for k, v in metadata.items() if k not in row})
            result.append(Observation(**row))
        return result


def _public_addresses(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise IngestionError("source hostname cannot be resolved") from exc
    addresses = sorted({info[4][0] for info in infos})
    for raw in addresses:
        address = ipaddress.ip_address(raw)
        if any((address.is_private, address.is_loopback, address.is_link_local, address.is_multicast, address.is_reserved, address.is_unspecified)):
            raise IngestionError("source resolves to a non-public network address")
    return addresses


class HTTPSourceClient:
    def __init__(self, *, timeout: float = 15.0, max_bytes: int = 5_000_000, allowed_hosts: frozenset[str] = frozenset()) -> None:
        if timeout <= 0 or max_bytes <= 0:
            raise ValueError("timeout and max_bytes must be positive")
        if not allowed_hosts:
            raise ValueError("allowed_hosts must be explicitly configured")
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.allowed_hosts = frozenset(host.lower().rstrip(".") for host in allowed_hosts)

    def fetch(self, url: str, *, source_id: str, dataset_id: str) -> tuple[bytes, dict[str, Any]]:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme != "https" or not hostname or hostname not in self.allowed_hosts:
            raise IngestionError("source URL must be HTTPS and match the configured official-source allowlist")
        _public_addresses(hostname)
        with httpx.Client(timeout=self.timeout, follow_redirects=False) as client:
            response = client.get(url, headers={"Accept": "application/json,text/csv"})
            response.raise_for_status()
            if len(response.content) > self.max_bytes:
                raise IngestionError("source response exceeds configured size limit")
            now = datetime.now(timezone.utc)
            last_modified = response.headers.get("Last-Modified")
            publication = parsedate_to_datetime(last_modified).astimezone(timezone.utc) if last_modified else now
            return response.content, {
                "source_id": source_id,
                "dataset_id": dataset_id,
                "source_version": response.headers.get("ETag", "unknown"),
                "revision": 0,
                "acquisition_time": now,
                "publication_time": min(publication, now),
                "provenance": (url,),
            }
