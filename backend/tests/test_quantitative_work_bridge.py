from app.quantitative_scientific_audit import IdentificationStatus, InferenceType, QuantitativeMethodAudit
from app.quantitative_work_bridge import work_from_quantitative_audit


def audit() -> QuantitativeMethodAudit:
    return QuantitativeMethodAudit(
        "M-Q1", "phenomenon", "does X improve forecast?", "target population", "outcome",
        ("x", "denominator"), ("count", "person-time"), "bounded", "assumptions",
        IdentificationStatus.PARTIALLY_IDENTIFIED, "estimator", ("sampling uncertainty",),
        ("alternative lag",), ("alternative model",), ("temporal holdout",),
        ("persistence",), ("candidate loses",), InferenceType.PREDICTIVE,
        ("causal effect",), ("source",),
    )


def test_quantitative_audit_generates_bounded_work_without_claiming_validation():
    work = work_from_quantitative_audit(audit())
    assert len(work) == 5
    assert all(item.status.value == "SPECIFIED" for item in work)
    assert all("causal effect" in item.capability_not_authorized for item in work)
    assert len({item.fingerprint for item in work}) == 5
