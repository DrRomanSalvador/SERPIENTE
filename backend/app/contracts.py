from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from math import isfinite
from typing import Any
from uuid import UUID, uuid4

def _finite(value: float, name: str) -> float:
    if not isfinite(value): raise ValueError(f"{name} must be finite")
    return float(value)
def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None: raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)

@dataclass(frozen=True, slots=True)
class Observation:
    source_id:str; dataset_id:str; variable_id:str; semantic_definition:str; unit:str; geography:str; event_time:datetime; publication_time:datetime; acquisition_time:datetime; source_version:str; revision:int; value:float|None; provenance:tuple[str,...]; denominator_id:str|None=None; quality:float=1.0; missing:bool=False; transformation_lineage:tuple[str,...]=(); observation_id:UUID|str=None
    def __post_init__(self)->None:
        object.__setattr__(self,"event_time",_utc(self.event_time,"event_time")); object.__setattr__(self,"publication_time",_utc(self.publication_time,"publication_time")); object.__setattr__(self,"acquisition_time",_utc(self.acquisition_time,"acquisition_time"))
        if self.event_time>self.acquisition_time: raise ValueError("event_time cannot be after acquisition_time")
        if self.publication_time>self.acquisition_time: raise ValueError("publication_time cannot be after acquisition_time")
        if self.revision<0: raise ValueError("revision must be non-negative")
        if self.missing:
            if self.value is not None: raise ValueError("missing observations must not carry a numeric value")
        elif self.value is None: raise ValueError("non-missing observations require a value")
        else: _finite(self.value,"value")
        q=_finite(self.quality,"quality")
        if not 0.0<=q<=1.0: raise ValueError("quality must be in [0,1]")
        if not self.source_id or not self.dataset_id or not self.variable_id or not self.semantic_definition: raise ValueError("source, dataset, variable and semantic definition are required")
        if not self.provenance: raise ValueError("provenance is required")
        object.__setattr__(self,"observation_id",self.observation_id or uuid4())
    def known_at(self,as_of:datetime)->bool:
        as_of=_utc(as_of,"as_of"); return self.acquisition_time<=as_of and self.publication_time<=as_of
    def to_dict(self)->dict[str,Any]:
        data=asdict(self); data["event_time"]=self.event_time.isoformat(); data["publication_time"]=self.publication_time.isoformat(); data["acquisition_time"]=self.acquisition_time.isoformat(); data["observation_id"]=str(self.observation_id); return data

@dataclass(frozen=True, slots=True)
class Event:
    event_id:UUID|str; event_time:datetime; geography:str; domain:str; event_type:str; magnitude:float; observation_ids:tuple[str,...]; provenance:tuple[str,...]
    def __post_init__(self)->None:
        object.__setattr__(self,"event_time",_utc(self.event_time,"event_time")); _finite(self.magnitude,"magnitude")
        if not self.observation_ids or not self.provenance: raise ValueError("event requires observation_ids and provenance")

@dataclass(frozen=True, slots=True)
class Signal:
    signal_id:UUID|str; event_id:UUID|str; domain:str; variable_id:str; value:float; z_score:float; anomaly_score:float; trend:float; acceleration:float; volatility:float; provenance:tuple[str,...]; event_time:datetime|None=None
    def __post_init__(self)->None:
        for name,value in (("value",self.value),("z_score",self.z_score),("anomaly_score",self.anomaly_score),("trend",self.trend),("acceleration",self.acceleration),("volatility",self.volatility)): _finite(value,name)
        if not self.domain or not self.variable_id: raise ValueError("signal domain and variable are required")
        if not 0<=self.anomaly_score<=1: raise ValueError("anomaly_score must be in [0,1]")
        if not self.provenance: raise ValueError("signal provenance is required")
        if self.event_time is not None: object.__setattr__(self,"event_time",_utc(self.event_time,"event_time"))

@dataclass(frozen=True, slots=True)
class Forecast:
    forecast_id:UUID|str; origin_time:datetime; horizon:str; target:str; probability:float; lower:float; upper:float; aleatoric:float; epistemic:float; measurement:float; parameter:float; structural:float; model_disagreement:float; regime:str; provenance:tuple[str,...]; point_in_time_fingerprint:str
    def __post_init__(self)->None:
        object.__setattr__(self,"origin_time",_utc(self.origin_time,"origin_time")); values=(self.probability,self.lower,self.upper,self.aleatoric,self.epistemic,self.measurement,self.parameter,self.structural,self.model_disagreement)
        if not all(isfinite(v) for v in values): raise ValueError("forecast values must be finite")
        if not 0<=self.probability<=1 or not 0<=self.model_disagreement<=1: raise ValueError("probability and model disagreement must be in [0,1]")
        if self.lower>self.upper or not self.provenance or not self.point_in_time_fingerprint: raise ValueError("invalid forecast interval, provenance or point-in-time fingerprint")

@dataclass(frozen=True, slots=True)
class Alert:
    alert_id:UUID|str; level:str; score:float; rationale:tuple[str,...]; event_ids:tuple[str,...]; signal_ids:tuple[str,...]; forecast_ids:tuple[str,...]; uncertainty:float; provenance:tuple[str,...]
    def __post_init__(self)->None:
        _finite(self.score,"score"); _finite(self.uncertainty,"uncertainty")
        if not 0<=self.score<=1 or not 0<=self.uncertainty<=1: raise ValueError("alert score and uncertainty must be in [0,1]")
        if not self.provenance: raise ValueError("alert provenance is required")
