"""Executable scientific discovery, falsification, and work-generation primitives."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Iterable
class KnowledgeState(StrEnum):
    UNKNOWN="UNKNOWN"; OBSERVATION="OBSERVATION"; MEASUREMENT="MEASUREMENT"; DESCRIPTION="DESCRIPTION"; ASSOCIATION="ASSOCIATION"; SIGNAL="SIGNAL"; PREDICTION="PREDICTION"; LATENT_STATE="LATENT_STATE"; HYPOTHESIS="HYPOTHESIS"; MODEL="MODEL"; MECHANISTIC_HYPOTHESIS="MECHANISTIC_HYPOTHESIS"; CAUSAL_EFFECT="CAUSAL_EFFECT"; DECISION_EVIDENCE="DECISION_EVIDENCE"; INTERVENTION_EVIDENCE="INTERVENTION_EVIDENCE"; OUTCOME="OUTCOME"; EVALUATED_OUTCOME="EVALUATED_OUTCOME"; REPLICATED="REPLICATED"; ESTABLISHED="ESTABLISHED"; REJECTED="REJECTED"; NOT_IDENTIFIABLE="NOT_IDENTIFIABLE"; OUTDATED="OUTDATED"; CONTRADICTED="CONTRADICTED"
class WorkStatus(StrEnum):
    DISCOVERED="DISCOVERED"; ANALYZED="ANALYZED"; SPECIFIED="SPECIFIED"; HANDOFF_READY="HANDOFF_READY"; IMPLEMENTED="IMPLEMENTED"; TESTED="TESTED"; VERIFIED="VERIFIED"; VALIDATED="VALIDATED"; ESTABLISHED="ESTABLISHED"; REJECTED="REJECTED"; SUPERSEDED="SUPERSEDED"
@dataclass(frozen=True,slots=True)
class ScientificClaim:
    claim_id:str; statement:str; state:KnowledgeState; evidence_ids:tuple[str,...]; assumptions:tuple[str,...]; provenance:tuple[str,...]; capability_authorized:tuple[str,...]; capability_not_authorized:tuple[str,...]
    def __post_init__(self)->None:
        if not self.claim_id.strip() or not self.statement.strip() or not self.provenance: raise ValueError("claim identity, statement and provenance are required")
        if not self.evidence_ids and self.state not in {KnowledgeState.UNKNOWN,KnowledgeState.HYPOTHESIS}: raise ValueError("non-hypothesis claim requires evidence")
        if not self.capability_not_authorized: raise ValueError("claim must define an authorization boundary")
@dataclass(frozen=True,slots=True)
class AlternativeExplanation:
    alternative_id:str; claim_id:str; explanation:str; discriminating_observations:tuple[str,...]; falsification_criteria:tuple[str,...]; provenance:tuple[str,...]
    def __post_init__(self)->None:
        if any(not value.strip() for value in (self.alternative_id,self.claim_id,self.explanation)): raise ValueError("alternative explanation is incomplete")
        if not self.discriminating_observations or not self.falsification_criteria or not self.provenance: raise ValueError("alternative requires discriminating observations, falsification and provenance")
@dataclass(frozen=True,slots=True)
class FalsificationTask:
    task_id:str; hypothesis_id:str; test_definition:str; failure_condition:str; stopping_rule:str; required_data:tuple[str,...]; temporal_requirement:str; provenance_requirement:str
    def __post_init__(self)->None:
        if any(not value.strip() for value in (self.task_id,self.hypothesis_id,self.test_definition,self.failure_condition,self.stopping_rule,self.temporal_requirement,self.provenance_requirement)) or not self.required_data: raise ValueError("falsification task is incomplete")
@dataclass(frozen=True,slots=True)
class ScientificWork:
    work_id:str; trigger:str; discovery:str; scientific_question:str; current_knowledge:str; uncertainty:str; alternative_explanations:tuple[str,...]; affected_object:str; mathematical_form:str; assumptions:tuple[str,...]; identifiability:str; data_required:tuple[str,...]; temporal_requirements:tuple[str,...]; falsification:tuple[str,...]; benchmark:tuple[str,...]; validation:tuple[str,...]; decision_relevance:float; expected_information_gain:float; cost:float; dependencies:tuple[str,...]; owner:str; status:WorkStatus; provenance:tuple[str,...]; stopping_rule:str; capability_not_authorized:tuple[str,...]
    def __post_init__(self)->None:
        if any(not value.strip() for value in (self.work_id,self.trigger,self.discovery,self.scientific_question,self.current_knowledge,self.uncertainty,self.affected_object,self.identifiability,self.owner,self.stopping_rule)): raise ValueError("scientific work has empty required identity field")
        if any(not isfinite(v) or v<0 for v in (self.decision_relevance,self.expected_information_gain,self.cost)): raise ValueError("work priority inputs must be finite and non-negative")
    @property
    def priority_proxy(self)->float: return float("inf") if self.cost==0 else self.expected_information_gain*self.decision_relevance/self.cost
    @property
    def fingerprint(self)->tuple[str,...]: return (self.trigger.strip().lower(),self.scientific_question.strip().lower(),self.affected_object.strip().lower(),self.identifiability.strip().lower(),tuple(sorted(x.strip().lower() for x in self.data_required)),tuple(sorted(x.strip().lower() for x in self.temporal_requirements)),tuple(sorted(x.strip().lower() for x in self.falsification)))
def prioritize_work(work_items:Iterable[ScientificWork])->tuple[ScientificWork,...]: return tuple(sorted(work_items,key=lambda w:(-w.priority_proxy,w.work_id)))
def deduplicate_work(work_items:Iterable[ScientificWork])->tuple[ScientificWork,...]:
    seen=set(); unique=[]
    for work in work_items:
        if work.fingerprint in seen: continue
        seen.add(work.fingerprint); unique.append(work)
    return tuple(unique)
def admissible_work(work:ScientificWork)->bool: return bool(work.provenance and work.alternative_explanations and work.falsification and work.benchmark and work.validation and work.stopping_rule.strip() and work.capability_not_authorized)
_ALLOWED_PROMOTIONS=frozenset({(KnowledgeState.UNKNOWN,KnowledgeState.OBSERVATION),(KnowledgeState.OBSERVATION,KnowledgeState.MEASUREMENT),(KnowledgeState.MEASUREMENT,KnowledgeState.DESCRIPTION),(KnowledgeState.DESCRIPTION,KnowledgeState.ASSOCIATION),(KnowledgeState.ASSOCIATION,KnowledgeState.PREDICTION),(KnowledgeState.PREDICTION,KnowledgeState.DECISION_EVIDENCE),(KnowledgeState.HYPOTHESIS,KnowledgeState.MODEL),(KnowledgeState.MODEL,KnowledgeState.PREDICTION),(KnowledgeState.MODEL,KnowledgeState.MECHANISTIC_HYPOTHESIS),(KnowledgeState.MECHANISTIC_HYPOTHESIS,KnowledgeState.CAUSAL_EFFECT),(KnowledgeState.CAUSAL_EFFECT,KnowledgeState.INTERVENTION_EVIDENCE),(KnowledgeState.OUTCOME,KnowledgeState.EVALUATED_OUTCOME),(KnowledgeState.EVALUATED_OUTCOME,KnowledgeState.REPLICATED),(KnowledgeState.REPLICATED,KnowledgeState.ESTABLISHED)})
def can_promote(current:KnowledgeState,target:KnowledgeState,*,criterion_satisfied:bool)->bool: return criterion_satisfied and (current,target) in _ALLOWED_PROMOTIONS
def adversarial_update(claim:ScientificClaim,*,interpretation_survived:bool|None,evidence_ids:tuple[str,...]=())->ScientificClaim:
    evidence=tuple(dict.fromkeys((*claim.evidence_ids,*evidence_ids)))
    if interpretation_survived is None: return ScientificClaim(claim.claim_id,claim.statement,claim.state,evidence,claim.assumptions,claim.provenance,claim.capability_authorized,claim.capability_not_authorized)
    state=claim.state if interpretation_survived else KnowledgeState.REJECTED
    return ScientificClaim(claim.claim_id,claim.statement,state,evidence,claim.assumptions,claim.provenance,claim.capability_authorized,claim.capability_not_authorized)
def scientific_impact_map(claim:ScientificClaim,alternatives:Iterable[AlternativeExplanation],tasks:Iterable[FalsificationTask])->dict[str,tuple[str,...]]:
    alts=tuple(a for a in alternatives if a.claim_id==claim.claim_id); task_ids=tuple(t.task_id for t in tasks if t.hypothesis_id==claim.claim_id)
    return {"claim":(claim.claim_id,),"state":(claim.state.value,),"evidence":claim.evidence_ids,"assumptions":claim.assumptions,"alternatives":tuple(a.alternative_id for a in alts),"falsification_tasks":task_ids,"authorized":claim.capability_authorized,"not_authorized":claim.capability_not_authorized}
__all__=["AlternativeExplanation","FalsificationTask","KnowledgeState","ScientificClaim","ScientificWork","WorkStatus","adversarial_update","admissible_work","can_promote","deduplicate_work","prioritize_work","scientific_impact_map"]
