from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import time
from typing import Any, Callable

from .contracts import Observation
from .ingestion import HTTPSourceClient
from .mapping import ObservationMapper


@dataclass(frozen=True, slots=True)
class PollJob:
    source_id: str
    dataset_id: str
    url: str
    interval_seconds: int

    def __post_init__(self) -> None:
        if not self.source_id or not self.dataset_id or not self.url or self.interval_seconds < 1:
            raise ValueError("poll job requires source, dataset, URL and positive interval")


class SourcePoller:
    def __init__(self, client: HTTPSourceClient, *, now: Callable[[], datetime] | None = None) -> None:
        self.client = client
        self.now = now or (lambda: datetime.now(timezone.utc))

    def poll_once(self, job: PollJob, mapper: ObservationMapper) -> list[Observation]:
        payload, metadata = self.client.fetch(job.url, source_id=job.source_id, dataset_id=job.dataset_id)
        raw = json.loads(payload)
        rows = raw if isinstance(raw, list) else raw.get("observations", [])
        if not isinstance(rows, list):
            raise ValueError("official source payload does not contain an observation list")
        acquired = metadata["acquisition_time"]
        publication = metadata["publication_time"]
        version = metadata["source_version"]
        provenance = tuple(metadata["provenance"])
        mapped: list[Observation] = []
        for row in rows:
            mapped.append(mapper.map_row(row, acquisition_time=acquired, publication_time=publication, provenance=provenance, source_version=version))
        return mapped

    def run(self, jobs: list[tuple[PollJob, ObservationMapper]], sink: Callable[[list[Observation]], Any], *, cycles: int = 1) -> None:
        if cycles < 1:
            raise ValueError("cycles must be positive")
        next_run = {job.source_id: 0.0 for job, _ in jobs}
        completed = 0
        while completed < cycles:
            now = time.monotonic()
            progressed = False
            for job, mapper in jobs:
                if now >= next_run[job.source_id]:
                    sink(self.poll_once(job, mapper))
                    next_run[job.source_id] = now + job.interval_seconds
                    progressed = True
                    completed += 1
                    if completed >= cycles:
                        break
            if not progressed:
                time.sleep(min(0.25, max(0.01, min(next_run.values()) - time.monotonic())))
