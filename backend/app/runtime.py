from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass
from typing import Iterable, Sequence
import numpy as np
from .contracts import Alert, Observation
from .engines import AlertEngine, EventEngine, PatternEngine, SignalEngine, TrajectoryEngine
from .interaction_validation import InteractionSpec, IncrementalPredictiveValue, PredictionRecord, compare_incremental_predictive_value
from .longitudinal import LongitudinalStateBuilder, PointInTimeStore
from .mapping import ObservationMapper
from .multihorizon import MultiHorizonForecaster
from .pit_binding import FeatureBinding, point_in_time_fingerprint
from .polling import PollJob, SourcePoller
from .prediction import LongitudinalForecaster, ValidationReport
from .quality import DataProcessMonitor
from .response import ResponseRecord
from .scientific_discovery_engine import ScientificWork, WorkStatus
from .scientific_protocol import ScientificValidationProtocol
from .scientific_work_execution import ScientificWorkResult, execute_forecast_outcome_scoring
from .outcomes import ForecastOutcome
from .runtime_scientific_bridge import work_from_runtime_object, execute_runtime_scientific_cycle
from .storage import RuntimeStore
from .supervised import LongitudinalSupervisedFrameBuilder
from .validation import drift_report, numerical_adversarial_check, temporal_leakage_check

@dataclass(frozen=True,slots=True)
class RuntimeResult:
    event_id:str; signal_ids:tuple[str,...]; pattern_id:str; trajectory_id:str; alert:Alert

class SerpienteRuntime:
    def __init__(self,*,store:RuntimeStore|None=None)->None:
        self.store=store; self.observations=PointInTimeStore(); self.state_builder=LongitudinalStateBuilder(); self.event_engine=EventEngine(); self.signal_engine=SignalEngine(); self.pattern_engine=PatternEngine(); self.trajectory_engine=TrajectoryEngine(); self.alert_engine=AlertEngine(); self.quality_monitor=DataProcessMonitor(); self.forecaster=LongitudinalForecaster(); self.multi_horizon:MultiHorizonForecaster|None=None; self.supervised_builder=LongitudinalSupervisedFrameBuilder(state_builder=self.state_builder)
        self.scientific_protocol=ScientificValidationProtocol(protocol_id="serpiente-predictive-v1",baseline="temporal prevalence and seasonal day-of-week baseline",temporal_holdout="60/20/20 chronological train/calibration/test split",calibration_method="logistic calibration on temporally separated calibration data",out_of_sample="final chronological holdout only",error_analysis="Brier score, log loss and ROC-AUC with preserved model comparison",model_comparison="calibrated logistic versus gradient boosting and baselines",adversarial_tests=("future leakage","non-finite values","malformed probabilities","point-in-time revision leakage"),drift_tests=("two-sample Kolmogorov-Smirnov distribution drift","regime/change-point screening"),prospective_plan="precommitted prospective deployment with point-in-time replay and outcome capture",causal_interpretation="prediction is not a causal effect and no causal effect is identified")

    def ingest(self,observations:Iterable[Observation])->int:
        rows=list(observations)
        if not rows: raise ValueError("at least one observation is required")
        if self.store:
            with self.store.transaction():
                for row in rows:
                    self.store.observation(row)
                    for work in work_from_runtime_object(row): self.store.scientific_work(work)
                    results,claim=execute_runtime_scientific_cycle(row)
                    for result in results: self.store.scientific_result(result)
                    self.store.scientific_claim(claim)
        self.observations.add(rows); return len(rows)

    def poll_once(self,client,job:PollJob,mapper:ObservationMapper)->int: return self.ingest(SourcePoller(client).poll_once(job,mapper))

    def process(self,*,as_of:datetime,geography:str,domain:str,event_type:str)->RuntimeResult:
        history=self.observations.history_at(as_of); current=[row for row in self.observations.at(as_of) if not row.missing]
        if not current: raise ValueError("no current non-missing observations available")
        state=self.state_builder.build(history,as_of=as_of); quality=self.quality_monitor.assess(history); provenance=tuple(dict.fromkeys(p for row in current for p in row.provenance)); magnitude=sum(abs(float(row.value)) for row in current)/len(current)
        event=self.event_engine.normalize(tuple(str(row.observation_id) for row in current),event_time=max(r.event_time for r in current),geography=geography,domain=domain,event_type=event_type,magnitude=magnitude,provenance=provenance)
        signals=[self.signal_engine.from_state(event,variable_id=variable,value=value,baseline=value-state.trends.get(variable,0.0),trend=state.trends.get(variable,0.0),acceleration=state.accelerations.get(variable,0.0),volatility=state.volatility.get(variable,0.0),provenance=provenance) for variable,value in state.values.items()]; pattern=self.pattern_engine.detect(signals); trajectory=self.trajectory_engine.build(pattern,signals,regime=state.regime); alert=self.alert_engine.build(trajectory,event_ids=(str(event.event_id),),signal_ids=tuple(str(s.signal_id) for s in signals),data_process_change=quality.process_change,data_process_reasons=quality.reasons)
        if self.store:
            with self.store.transaction():
                self.store.event(event)
                for signal in signals: self.store.signal(signal)
                self.store.alert(alert)
        return RuntimeResult(str(event.event_id),tuple(str(s.signal_id) for s in signals),pattern.pattern_id,trajectory.trajectory_id,alert)

    def record_outcome(self,outcome:ForecastOutcome)->ScientificWorkResult:
        if self.store is None: raise RuntimeError("outcome persistence requires a runtime store")
        work=ScientificWork(work_id=f"forecast-outcome:{outcome.prediction_id}",trigger="realized-forecast-outcome",discovery="forecast outcome became available",scientific_question="how did the forecast score on the realized outcome?",current_knowledge="one realized forecast-outcome pair",uncertainty="aggregate calibration, discrimination and generalization remain unresolved",alternative_explanations=("pairwise forecast error is idiosyncratic","pairwise error reflects systematic miscalibration"),affected_object=outcome.prediction_id,mathematical_form="Brier=(p-y)^2; logloss=-[y log p+(1-y)log(1-p)]",assumptions=("binary target","outcome follows forecast origin"),identifiability="pairwise scoring identifiable",data_required=("forecast","outcome"),temporal_requirements=(f"origin_time={outcome.origin_time.isoformat()}",f"outcome_time={outcome.outcome_time.isoformat()}"),falsification=("pairwise score is exactly reproducible from the forecast and outcome"),benchmark=("paired baseline required for incremental predictive value"),validation=("aggregate scoring over eligible forecasts","calibration on temporally separated data"),decision_relevance=1.0,expected_information_gain=1.0,cost=1.0,dependencies=(),owner="ESPIA",status=WorkStatus.SPECIFIED,provenance=outcome.provenance,stopping_rule="score the pair and do not promote to calibration or validation",capability_not_authorized=("calibration from a single pair","incremental predictive value without a paired baseline","causal effect"))
        with self.store.transaction():
            self.store.outcome(outcome)
            result=execute_forecast_outcome_scoring(work,outcome)
            self.store.scientific_work(work); self.store.scientific_result(result)
        return result

    def record_response(self,response:ResponseRecord)->None:
        if self.store is None: raise RuntimeError("response persistence requires a runtime store")
        with self.store.transaction(): self.store.response(response)

    def train(self,frame)->ValidationReport:
        if "target_time" in frame.columns:
            finding=temporal_leakage_check(frame)
            if not finding.passed: raise ValueError(finding.reason)
        numeric=frame.select_dtypes(include=[np.number]).drop(columns=["target"],errors="ignore")
        if numeric.empty: raise ValueError("scientific training requires at least one numeric predictor")
        finite=numerical_adversarial_check(numeric.to_numpy(dtype=float).ravel())
        if not finite.passed: raise ValueError(finite.reason)
        if len(numeric)>=10:
            drift=drift_report(numeric.iloc[:len(numeric)//2,0],numeric.iloc[len(numeric)//2:,0])
            if drift["drift_detected"]: pass
        return self.forecaster.fit(frame)
    def train_from_observations(self,observations:Iterable[Observation],*,target_variable:str,horizon_steps:int=1)->ValidationReport: return self.train(self.supervised_builder.build(observations,target_variable=target_variable,horizon_steps=horizon_steps))
    def train_multi_horizon(self,frames:dict[str,object])->dict[str,ValidationReport]: self.multi_horizon=MultiHorizonForecaster(tuple(frames.keys())); return self.multi_horizon.fit(frames)
    def forecast(self,features,*,feature_bindings:tuple[FeatureBinding,...],origin_time:datetime,target:str,horizon:str,regime:str,provenance:tuple[str,...]):
        if origin_time.tzinfo is None: raise ValueError("origin_time must be timezone-aware")
        fingerprint=point_in_time_fingerprint(features,feature_bindings,origin_time=origin_time); forecast=self.forecaster.forecast(features,feature_bindings=feature_bindings,origin_time=origin_time,target=target,horizon=horizon,regime=regime,provenance=provenance,point_in_time_fingerprint=fingerprint)
        if self.store:
            with self.store.transaction(): self.store.forecast(forecast)
        return forecast
    def evaluate_interaction(self,interaction:InteractionSpec,baseline:Sequence[PredictionRecord],interaction_model:Sequence[PredictionRecord],outcomes:Sequence[int])->IncrementalPredictiveValue: return compare_incremental_predictive_value(interaction,baseline,interaction_model,outcomes)
    def forecast_multi_horizon(self,features:dict[str,object],*,feature_bindings:dict[str,tuple[FeatureBinding,...]],origin_time:datetime,target:str,regime:str,provenance:tuple[str,...]):
        if self.multi_horizon is None: raise RuntimeError("multi-horizon models must be trained before forecasting")
        if origin_time.tzinfo is None: raise ValueError("origin_time must be timezone-aware")
        forecasts=self.multi_horizon.forecast(features,feature_bindings=feature_bindings,origin_time=origin_time,target=target,regime=regime,provenance=provenance)
        if self.store:
            with self.store.transaction():
                for forecast in forecasts: self.store.forecast(forecast)
        return forecasts
