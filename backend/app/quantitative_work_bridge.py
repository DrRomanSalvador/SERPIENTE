"""Translate quantitative audit deficits into bounded ScientificWork candidates."""
from __future__ import annotations
import hashlib
from .quantitative_scientific_audit import QuantitativeMethodAudit
from .scientific_discovery_engine import ScientificWork, WorkStatus, deduplicate_work

def work_from_quantitative_audit(audit:QuantitativeMethodAudit,*,owner:str="ESPIA")->tuple[ScientificWork,...]:
    candidates=[]; dimensions=(("identification",audit.identification.value,"resolve identification status"),("uncertainty","; ".join(audit.uncertainty),"quantify uncertainty"),("sensitivity","; ".join(audit.sensitivity),"execute sensitivity analysis"),("robustness","; ".join(audit.robustness),"test robustness"),("validation","; ".join(audit.validation),"execute validation design")); temporal_requirements=audit.temporal_requirements or ("preserve information cutoff and outcome time",)
    for dimension,requirement,question_suffix in dimensions:
        semantic_seed="|".join((audit.method_id,dimension,audit.scientific_question,requirement,*audit.predictor_definitions,*temporal_requirements,*audit.falsification)); version=hashlib.sha256(semantic_seed.encode("utf-8")).hexdigest()[:12]
        candidates.append(ScientificWork(work_id=f"{audit.method_id}:{dimension}:{version}",trigger=f"quantitative-audit:{audit.method_id}:{dimension}",discovery=requirement,scientific_question=f"{audit.scientific_question}; {question_suffix}",current_knowledge=f"inference={audit.inference_type.value}; identification={audit.identification.value}",uncertainty=requirement,alternative_explanations=("the unresolved dimension reflects the hypothesized phenomenon","the unresolved dimension reflects observation, measurement, denominator, temporal, or model error"),affected_object=audit.method_id,mathematical_form="audit -> falsifiable quantitative work",assumptions=audit.assumptions,identifiability=audit.identification.value,data_required=audit.predictor_definitions,temporal_requirements=temporal_requirements,falsification=audit.falsification,benchmark=audit.benchmarks,validation=audit.validation,decision_relevance=1.0,expected_information_gain=1.0,cost=1.0,dependencies=(audit.method_id,),owner=owner,status=WorkStatus.SPECIFIED,provenance=audit.provenance,stopping_rule=f"close {dimension} work only when its stated evidence requirement is satisfied or explicitly shown non-identifiable",capability_not_authorized=audit.capability_not_authorized))
    return deduplicate_work(candidates)

__all__=["work_from_quantitative_audit"]
