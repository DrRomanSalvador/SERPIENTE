from __future__ import annotations
import hmac,json,os,time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime,timezone
from typing import AsyncIterator
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from .contracts import Observation
from .outcomes import ForecastOutcome
from .response import ResponseRecord
from .runtime import SerpienteRuntime
from .storage_factory import create_runtime_store
MAX_BODY_BYTES=2_000_000; RATE_LIMIT=60; WINDOW_SECONDS=60

def _credentials()->dict[str,str]:
    raw=os.getenv("SERPIENTE_API_KEYS_JSON","{}")
    try: parsed=json.loads(raw)
    except json.JSONDecodeError as exc: raise RuntimeError("SERPIENTE_API_KEYS_JSON is invalid") from exc
    if not isinstance(parsed,dict): raise RuntimeError("SERPIENTE_API_KEYS_JSON must be an object")
    return {str(k):str(v) for k,v in parsed.items() if str(v) in {"INGESTOR","ANALYST","ADMIN"}}

def _role(request:Request,required:set[str])->str:
    provided=request.headers.get("X-SERPIENTE-API-Key","")
    for key,role in _credentials().items():
        if hmac.compare_digest(provided,key):
            if role not in required and role!="ADMIN": raise HTTPException(403,"insufficient role")
            return role
    raise HTTPException(401,"authentication required")

class ObservationInput(BaseModel):
    source_id:str=Field(min_length=1,max_length=200); dataset_id:str=Field(min_length=1,max_length=200); variable_id:str=Field(min_length=1,max_length=200); semantic_definition:str=Field(min_length=1,max_length=2000); unit:str=Field(min_length=1,max_length=100); geography:str=Field(min_length=1,max_length=200); event_time:str; publication_time:str; acquisition_time:str; source_version:str=Field(min_length=1,max_length=200); revision:int=Field(ge=0); value:float|None=Field(default=None,allow_inf_nan=False); provenance:list[str]=Field(min_length=1,max_length=20); denominator_id:str|None=Field(default=None,max_length=200); quality:float=Field(default=1.0,ge=0.0,le=1.0,allow_inf_nan=False); missing:bool=False; transformation_lineage:list[str]=Field(default_factory=list,max_length=20)
class ProcessInput(BaseModel):
    as_of:str; geography:str=Field(min_length=1,max_length=200); domain:str=Field(min_length=1,max_length=100); event_type:str=Field(min_length=1,max_length=100)
class OutcomeInput(BaseModel):
    prediction_id:str=Field(min_length=1,max_length=200); outcome_time:datetime; target:str=Field(min_length=1,max_length=200); observed:int=Field(ge=0,le=1); provenance:list[str]=Field(min_length=1,max_length=20)
class ResponseInput(BaseModel):
    response_id:str=Field(min_length=1,max_length=200); alert_id:str=Field(min_length=1,max_length=200); prediction_id:str|None=Field(default=None,max_length=200); decision_id:str=Field(min_length=1,max_length=200); decision_time:datetime; action_id:str=Field(min_length=1,max_length=200); action_time:datetime; response_eligible:bool; intended_mechanism:str=Field(min_length=1,max_length=2000); response_delay_seconds:float=Field(ge=0); intervention_exposure:str=Field(min_length=1,max_length=2000); implementation_failure:str|None=Field(default=None,max_length=2000); resource_capacity_constraints:str|None=Field(default=None,max_length=2000); outcome_id:str|None=Field(default=None,max_length=200); outcome_time:datetime|None=None; response_horizon:str=Field(min_length=1,max_length=200); causal_status:str=Field(min_length=1,max_length=200); provenance:list[str]=Field(min_length=1,max_length=20)

@asynccontextmanager
async def lifespan(app:FastAPI)->AsyncIterator[None]:
    app.state.runtime=SerpienteRuntime(store=create_runtime_store()); app.state.rate=defaultdict(list)
    try: yield
    finally: app.state.runtime.store.close()
app=FastAPI(title="SERPIENTE",version="0.1.0",lifespan=lifespan)

@app.middleware("http")
async def request_limits(request:Request,call_next):
    if request.method in {"POST","PUT","PATCH"}:
        body=await request.body()
        if len(body)>MAX_BODY_BYTES: return JSONResponse(status_code=413,content={"error":"request_too_large"})
        key=request.headers.get("X-SERPIENTE-API-Key",""); client_host=request.client.host if request.client else "unknown"; identity=f"{client_host}:{key}"; now=time.monotonic(); hits=[t for t in request.app.state.rate[identity] if now-t<WINDOW_SECONDS]
        if len(hits)>=RATE_LIMIT: return JSONResponse(status_code=429,content={"error":"rate_limit_exceeded"})
        hits.append(now); request.app.state.rate[identity]=hits
    return await call_next(request)

@app.get("/health")
async def health(): return {"status":"healthy","service":"SERPIENTE"}
@app.get("/ready")
async def ready(request:Request): return {"status":"ready","runtime":request.app.state.runtime.store.snapshot()}
@app.post("/v1/observations")
async def ingest(request:Request,observations:list[ObservationInput]):
    _role(request,{"INGESTOR","ANALYST"})
    rows=[Observation(**{**item.model_dump(),"event_time":datetime.fromisoformat(item.event_time),"publication_time":datetime.fromisoformat(item.publication_time),"acquisition_time":datetime.fromisoformat(item.acquisition_time),"provenance":tuple(item.provenance),"transformation_lineage":tuple(item.transformation_lineage)}) for item in observations]
    return {"accepted":request.app.state.runtime.ingest(rows)}
@app.post("/v1/process")
async def process(request:Request,payload:ProcessInput):
    _role(request,{"ANALYST"}); result=request.app.state.runtime.process(as_of=datetime.fromisoformat(payload.as_of),geography=payload.geography,domain=payload.domain,event_type=payload.event_type)
    return {"event_id":result.event_id,"signal_ids":result.signal_ids,"pattern_id":result.pattern_id,"trajectory_id":result.trajectory_id,"alert":{"alert_id":str(result.alert.alert_id),"level":result.alert.level,"score":result.alert.score,"uncertainty":result.alert.uncertainty,"provenance":result.alert.provenance}}
@app.post("/v1/outcomes")
async def record_outcome(request:Request,payload:OutcomeInput):
    _role(request,{"ANALYST"}); stored=request.app.state.runtime.store.forecast_payload(payload.prediction_id)
    if stored is None: raise HTTPException(404,"prediction_id does not reference a persisted forecast")
    origin=datetime.fromisoformat(stored["origin_time"])
    if stored["target"]!=payload.target: raise HTTPException(422,"outcome target does not match forecast target")
    outcome=ForecastOutcome(payload.prediction_id,origin,payload.outcome_time,payload.target,payload.observed,float(stored["probability"]),stored["horizon"],tuple(payload.provenance))
    with request.app.state.runtime.store.transaction(): request.app.state.runtime.store.outcome(outcome)
    return {"prediction_id":outcome.prediction_id,"brier_error":round(outcome.brier_error,12),"log_loss_error":round(outcome.log_loss_error,12),"outcome_time":outcome.outcome_time.astimezone(timezone.utc).isoformat()}
@app.post("/v1/responses")
async def record_response(request:Request,payload:ResponseInput):
    _role(request,{"ANALYST"})
    try: response=ResponseRecord(**{**payload.model_dump(),"provenance":tuple(payload.provenance)}); request.app.state.runtime.record_response(response)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    return {"response_id":response.response_id,"alert_id":response.alert_id,"decision_id":response.decision_id,"action_id":response.action_id,"causal_status":response.causal_status}

def main()->None:
    import uvicorn
    uvicorn.run("app.main:app",host=os.getenv("SERPIENTE_HOST","127.0.0.1"),port=int(os.getenv("SERPIENTE_PORT","8001")))
