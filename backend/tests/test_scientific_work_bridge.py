from app.scientific_validation_contracts import FalsificationCriterion, ValidationContract, ValidationStage
from app.scientific_work_bridge import work_from_validation_contract


def contract() -> ValidationContract:
    criterion = FalsificationCriterion(
        "F1",
        "candidate adds predictive information",
        "blocked temporal comparison",
        "candidate loses against baseline",
        "candidate improves predefined metric",
        ("outcome", "candidate", "baseline"),
        "strict temporal holdout",
        "immutable PIT provenance",
    )
    return ValidationContract(
        "VC1",
        "interaction-x-y",
        ValidationStage.TESTED,
        ValidationStage.PROSPECTIVE_VALIDATION_REQUIRED,
        "rolling-origin",
        ("persistence", "seasonal"),
        ("brier", "log_loss"),
        "calibration assessed separately",
        "all features available by cutoff",
        "external cohort required",
        "prospective registration required",
        (criterion,),
        ("spec-v1",),
    )


def test_validation_contract_materializes_executable_scientific_work():
    work = work_from_validation_contract(contract())
    assert len(work) == 1
    assert work[0].work_id == "VC1:F1"
    assert work[0].status.value == "SPECIFIED"
    assert work[0].falsification == ("candidate loses against baseline",)
    assert "all features available by cutoff" in work[0].assumptions
    assert "causal effect inference from validation performance alone" in work[0].capability_not_authorized


def test_repeated_contract_generation_is_semantically_deduplicated():
    first = work_from_validation_contract(contract())
    second = work_from_validation_contract(contract())
    assert first[0].fingerprint == second[0].fingerprint
