from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml


@dataclass(frozen=True, slots=True)
class SourceDefinition:
    source_id: str
    authority: str
    host: str
    scheme: str
    api_key_env: str | None
    geography: str
    domains: tuple[str, ...]
    endpoint_family: str
    revision_policy: str


class OfficialSourceRegistry:
    def __init__(self, path: str | Path) -> None:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not isinstance(raw.get("sources"), dict):
            raise ValueError("official source registry is malformed")
        self.sources: dict[str, SourceDefinition] = {}
        for source_id, item in raw["sources"].items():
            if not isinstance(item, dict):
                raise ValueError(f"source {source_id} is malformed")
            host = str(item["host"]).lower().rstrip(".")
            scheme = str(item["scheme"]).lower()
            if scheme != "https" or not host or not str(item["authority"]).strip():
                raise ValueError(f"source {source_id} must use HTTPS and identify an authority")
            self.sources[source_id] = SourceDefinition(source_id, str(item["authority"]), host, scheme, item.get("api_key_env"), str(item["geography"]), tuple(item.get("domains", ())), str(item["endpoint_family"]), str(item["revision_policy"]))

    def hosts(self) -> frozenset[str]:
        return frozenset(source.host for source in self.sources.values())

    def require_credentials(self, source_id: str) -> str | None:
        source = self.sources[source_id]
        if not source.api_key_env:
            return None
        value = os.getenv(source.api_key_env, "").strip()
        if not value:
            raise RuntimeError(f"credential {source.api_key_env} is required for source {source_id}")
        return value
