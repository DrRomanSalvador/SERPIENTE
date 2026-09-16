"""Execute bounded scientific work against concrete SERPIENTE runtime objects."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from math import log
from .contracts import Forecast, Observation, Signal
from .outcomes import ForecastOutcome
from .scientific_discovery_engine import ScientificWork
class ExecutionOutcome(StrEnum): EXECUTED="EXECUTED"; INCONCLUSIVE="INCONCLUSIVE"; REJECTED="REJECTED"; BLOCKED_EXTERNAL="BLOCKED_EXTERNAL"
@dataclass(frozen=True,slots=True)
class ScientificWorkResult:
    work_id:str; runtime_id:str; outcome:ExecutionOutcome; finding:str; evidence:tuple[str,...]; epistemic_state:str; new_work_required:bool; capability_not_authorized:tuple[str,...]; provenance:tuple[str,...]
    def __post_init__(self)->None:
        if not self.work_id or not self.runtime_id or not self.finding: raise ValueError("execution result identity and finding are required")
        if not self.evidence or not self.provenance: raise ValueError("execution result requires evidence and provenance")
        if not self.capability_not_authorized: raise ValueError("execution result requires capability boundary")
def _runtime_id(obj:Observation|Signal|Forecast)->str: return str(obj.observation_id if isinstance(obj,Observation) else obj.signal_id if isinstance(obj,Signal) else obj.forecast_id)
def _base_result(work:ScientificWork,obj:Observation|Signal|Forecast,outcome:ExecutionOutcome,finding:str,evidence:tuple[str,...],state:str,new_work:bool)->ScientificWorkResult: return ScientificWorkResult(work.work_id,_runtime_id(obj),outcome,finding,evidence,state,new_work,work.capability_not_authorized,tuple(dict.fromkeys((*work.provenance,f"runtime:{_runtime_id(obj)}"))))
def execute_scientific_work(work:ScientificWork,obj:Observation|Signal|Forecast)->ScientificWorkResult:
    if isinstance(obj,Observation):
        temporal_ok=obj.event_time<=obj.publication_time<=obj.acquisition_time
        if not temporal_ok: return _base_result(work,obj,ExecutionOutcome.REJECTED,"observation temporal ordering is invalid",(f"event_time={obj.event_time.isoformat()}",f"publication_time={obj.publication_time.isoformat()}",f"acquisition_time={obj.acquisition_time.isoformat()}"),"REJECTED",False)
        return _base_result(work,obj,ExecutionOutcome.INCONCLUSIVE,"observation contract is temporally coherent and provenance-bearing; a single observation cannot distinguish phenomenon drift from measurement, reporting, denominator, coverage, or ascertainment drift",(f"source={obj.source_id}",f"dataset={obj.dataset_id}",f"variable={obj.variable_id}",f"revision={obj.revision}",f"known_at_acquisition={obj.known_at(obj.acquisition_time)}"),"OBSERVATION",False)
    if isinstance(obj,Signal):
        if obj.event_time is None: return _base_result(work,obj,ExecutionOutcome.INCONCLUSIVE,"signal is numerically well-formed and provenance-bearing, but no event timestamp is available; temporal precedence, lead time, and change-point claims are not identifiable from this object",(f"anomaly_score={obj.anomaly_score}",f"trend={obj.trend}",f"acceleration={obj.acceleration}",f"volatility={obj.volatility}"),"SIGNAL",False)
        return _base_result(work,obj,ExecutionOutcome.INCONCLUSIVE,"signal carries event_time, so temporal ordering is representable; one signal alone still cannot establish a phenomenon change or predictive lead time",(f"event_time={obj.event_time.isoformat()}",f"anomaly_score={obj.anomaly_score}",f"trend={obj.trend}",f"acceleration={obj.acceleration}",f"volatility={obj.volatility}"),"SIGNAL",False)
    probability_ok=0.0<=obj.probability<=1.0; interval_ok=obj.lower<=obj.upper; pit_present=bool(obj.point_in_time_fingerprint)
    if not(probability_ok and interval_ok and pit_present): return _base_result(work,obj,ExecutionOutcome.REJECTED,"forecast contract fails a structural validity check",(f"probability_ok={probability_ok}",f"interval_ok={interval_ok}",f"pit_present={pit_present}"),"REJECTED",False)
    return _base_result(work,obj,ExecutionOutcome.BLOCKED_EXTERNAL,"forecast is structurally eligible, but predictive scoring requires an outcome observed after forecast origin; no outcome is carried by the runtime Forecast object",(f"origin_time={obj.origin_time.isoformat()}",f"horizon={obj.horizon}",f"target={obj.target}",f"pit={obj.point_in_time_fingerprint}"),"PREDICTION",False)
def execute_forecast_outcome_scoring(work:ScientificWork,outcome:ForecastOutcome)->ScientificWorkResult:
    brier=outcome.brier_error; p=min(max(outcome.predicted_probability,1e-8),1-1e-8); log_loss=float(-(outcome.observed*log(p)+(1-outcome.observed)*log(1-p))); provenance=tuple(dict.fromkeys((*work.provenance,*outcome.provenance,f"outcome:{outcome.prediction_id}")))
    return ScientificWorkResult(work.work_id,outcome.prediction_id,ExecutionOutcome.EXECUTED,f"single forecast-outcome pair scored: brier={brier:.12g}; log_loss={log_loss:.12g}; single-pair scoring does not establish calibration, discrimination, generalization, or prospective validity",(f"origin_time={outcome.origin_time.isoformat()}",f"outcome_time={outcome.outcome_time.isoformat()}",f"target={outcome.target}",f"horizon={outcome.horizon}",f"observed={outcome.observed}",f"predicted_probability={outcome.predicted_probability}",f"brier={brier:.12g}",f"log_loss={log_loss:.12g}"),"EVALUATED_OUTCOME",False,tuple(dict.fromkeys((*work.capability_not_authorized,"calibration from a single pair","incremental predictive value without a paired baseline"))),provenance)
__all__=["ExecutionOutcome","ScientificWorkResult","execute_scientific_work","execute_forecast_outcome_scoring"]
