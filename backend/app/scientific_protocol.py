from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScientificValidationProtocol:
    protocol_id: str
    baseline: str
    temporal_holdout: str
    calibration_method: str
    out_of_sample: str
    error_analysis: str
    model_comparison: str
    adversarial_tests: tuple[str, ...]
    drift_tests: tuple[str, ...]
    prospective_plan: str
    causal_interpretation: str

    def __post_init__(self) -> None:
        required = (self.protocol_id, self.baseline, self.temporal_holdout, self.calibration_method, self.out_of_sample, self.error_analysis, self.model_comparison, self.prospective_plan, self.causal_interpretation)
        if any(not value.strip() for value in required):
            raise ValueError("scientific validation protocol is incomplete")
        if not self.adversarial_tests or not self.drift_tests:
            raise ValueError("scientific validation protocol requires adversarial and drift tests")
        if "causal" not in self.causal_interpretation.lower() or "not" not in self.causal_interpretation.lower():
            raise ValueError("predictive protocol must explicitly separate prediction from causation")
