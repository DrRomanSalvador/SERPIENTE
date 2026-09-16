import numpy as np
import pytest
from app.quantitative_scientific_audit import BiasAudit,DenominatorSpec,EvidenceDependency,IdentificationStatus,InferenceType,ObservationModelSpec,QuantitativeMethodAudit,SensitivityScenario,brier_skill_score,calibration_in_the_large,evidence_independence_matrix,interval_width,lagged_pair

def test_quantitative_audit_requires_full_epistemic_boundary():
    audit=QuantitativeMethodAudit("M1","phenomenon","question","target population","outcome",("x",),("count",),"real-valued",("assumption",),IdentificationStatus.PARTIALLY_IDENTIFIED,"estimator",("sampling",),("denominator sensitivity",),("robust estimator",),("temporal holdout",),("persistence",),("failure if worse than baseline",),InferenceType.PREDICTIVE,("causal effect",),("source",))
    assert audit.identification is IdentificationStatus.PARTIALLY_IDENTIFIED; assert audit.inference_type is InferenceType.PREDICTIVE

def test_denominator_and_observation_models_require_explicit_processes():
    denominator=DenominatorSpec("D1","target","exposed","observed","eligible","30 days","Ceuta","mobility tracked","clinical ascertainment","cases","population","uncertain",("source",)); observation=ObservationModelSpec("O1","S_t","Y_t","diagnostic","D1","reporting","coverage","Y_t ~ p(Y_t | S_t,O_t,D_t,R_t,C_t)",( "reporting drift",),("coverage audit",),("source",)); assert denominator.denominator_id=="D1"; assert "S_t" in observation.equation

def test_bias_and_sensitivity_are_structured_not_free_text_flags():
    bias=BiasAudit("B1","selection","possible","plausible","unknown","not estimated","weighting","material",("source",)); scenario=SensitivityScenario("S1","case definition","broader definition","risk","parallel ascertainment","material divergence",("source",)); assert bias.mitigation=="weighting"; assert scenario.falsification_condition=="material divergence"

def test_evidence_dependency_marks_shared_lineage():
    items=[EvidenceDependency("E1","S1","D1","A1","M1","ME1","I1",("p",)),EvidenceDependency("E2","S2","D1","A2","M2","ME2","I2",("p",)),EvidenceDependency("E3","S3","D3","A3","M3","ME3","I3",("p",))]; matrix=evidence_independence_matrix(items); assert np.array_equal(matrix,np.array([[1,1,0],[1,1,0],[0,0,1]]))

def test_predictive_metrics_separate_skill_calibration_and_sharpness():
    y=[0,1,1,0]; baseline=[0.5]*4; candidate=[0.1,0.9,0.8,0.2]; assert brier_skill_score(y,baseline,candidate)>0; assert calibration_in_the_large(y,candidate)==pytest.approx(0.0); assert interval_width([0,0,1,1],[1,2,3,4])==pytest.approx(2.0)

def test_lagged_pair_preserves_direction():
    a,b=lagged_pair([1,2,3,4],1); assert np.array_equal(a,[1,2,3]); assert np.array_equal(b,[2,3,4])

def test_invalid_probability_or_interval_inputs_fail_closed():
    with pytest.raises(ValueError): calibration_in_the_large([0,1],[0.2,1.2])
    with pytest.raises(ValueError): interval_width([2],[1])
