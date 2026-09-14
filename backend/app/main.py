from __future__ import annotations

import hmac
import json
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .contracts import Observation
from .runtime import SerpienteRuntime
from .storage import RuntimeStore

MAX_BODY_BYTES = 2_000_000
RATE_LIMIT = 60
WINDOW_SECONDS = 60


def _credentials() -> dict[str, str]:
    raw = os.getenv("SERPIENTE_API_KEYS_JSON", "{}")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("SERPIENTE_API_KEYS_JSON is invalid") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("SERPIENTE_API_KEYS_JSON must be an object")
    return {str(k): str(v) for k, v in parsed.items() if str(v) in {"INGESTOR", "ANALYST", "ADMIN"}}


def _role(request: Request, required: set[str]) -> str:
    provided = request.headers.get("X-SERPIENTE-API-Key", "")
    for key, role in _credentials().items():
        if hmac.compare_digest(provided, key):
            if role not in required and role != "ADMIN":
                raise HTTPException(403, "insufficient role")
            return role
    raise HTTPException(401, "authentication required")


class ObservationInput(BaseModel):
    source_id: str = Field(min_length=1, max_length=200)
    dataset_id: str = Field(min_length=1, max_length=200)
    variable_id: str = Field(min_length=1, max_length=200)
    semantic_definition: str = Field(min_length=1, max_length=2000)
    unit: str = Field(min_length=1, max_length=100)
    geography: str = Field(min_length=1, max_length=200)
    event_time: str
    publication_time: str
    acquisition_time: str
    source_version: str = Field(min_length=1, max_length=200)
    revision: int = Field(ge=0)
    value: float
    provenance: list[str] = Field(min_length=1, max_length=20)
    quality: float = Field(default=1.0, ge=0.0, le=1.0)
    missing: bool = False
    transformation_lineage: list[str] = Field(default_factory=list, max_length=20)


class ProcessInput(BaseModel):
    as_of: str
    geography: str = Field(min_length=1, max_length=200)
    domain: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=100)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    path = os.getenv("SERPIENTE_RUNTIME_DB", "serpiente-runtime.sqlite3")
    app.state.runtime = SerpienteRuntime(store=RuntimeStore(path))
    app.state.rate = defaultdict(list)
    try:
        yield
    finally:
        app.state.runtime.store.close()


app = FastAPI(title="SERPIENTE", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def request_limits(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        length = request.headers.get("content-length")
        if length and int(length) > MAX_BODY_BYTES:
            raise HTTPException(413, "request too large")
        key = request.headers.get("X-SERPIENTE-API-Key", "")
        now = time.monotonic()
        hits = [t for t in request.app.state.rate[key] if now - t < WINDOW_SECONDS]
        if len(hits) >= RATE_LIMIT:
            raise HTTPException(429, "rate limit exceeded")
        hits.append(now)
        request.app.state.rate[key] = hits
    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SERPIENTE"}


@app.get("/ready")
async def ready(request: Request):
    return {"status": "ready", "runtime": request.app.state.runtime.store.snapshot()}


@app.post("/v1/observations")
async def ingest(request: Request, observations: list[ObservationInput]):
    _role(request, {"INGESTOR", "ANALYST"})
    from datetime import datetime
    rows = [Observation(**{**item.model_dump(), "event_time": datetime.fromisoformat(item.event_time), "publication_time": datetime.fromisoformat(item.publication_time), "acquisition_time": datetime.fromisoformat(item.acquisition_time), "provenance": tuple(item.provenance), "transformation_lineage": tuple(item.transformation_lineage)}) for item in observations]
    return {"accepted": request.app.state.runtime.ingest(rows)}


@app.post("/v1/process")
async def process(request: Request, payload: ProcessInput):
    _role(request, {"ANALYST"})
    from datetime import datetime
    result = request.app.state.runtime.process(as_of=datetime.fromisoformat(payload.as_of), geography=payload.geography, domain=payload.domain, event_type=payload.event_type)
    return {"event_id": result.event_id, "signal_ids": result.signal_ids, "pattern_id": result.pattern_id, "trajectory_id": result.trajectory_id, "alert": result.alert.__dict__ if hasattr(result.alert, "__dict__") else {"alert_id": str(result.alert.alert_id), "level": result.alert.level, "score": result.alert.score, "uncertainty": result.alert.uncertainty, "provenance": result.alert.provenance}}
