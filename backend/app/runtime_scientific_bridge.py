"""Bridge concrete SERPIENTE runtime objects into executable scientific work.

This module deliberately consumes real runtime contracts (Observation, Signal,
Forecast) rather than inventing a parallel discovery input format. It produces
bounded ScientificWork candidates; it does not promote observations to truth,
forecasts to validity, or associations to causality.
"""
from __future__ import annotations

from typing import TypeAlias

from .contracts import Forecast, Observation, Signal
from .quantitative_scientific_audit import IdentificationStatus, InferenceType, QuantitativeMethodAudit
from .quantitative_work_bridge import work_from_quantitative_audit
from .scientific_discovery_engine import ScientificWork

RuntimeObject: TypeAlias = Observation | Signal | Forecast


def _provenance(obj: RuntimeObject) -> tuple[str, ...]:
    return tuple(dict.fromkeys(obj.provenance))


def _runtime_identity(obj: RuntimeObject) -> str:
    if isinstance(obj, Observation):
        return str(obj.observation_id)
    if isinstance(obj, Signal):
        return str(obj.signal_id)
    return str(obj.forecast_id)


def quantitative_audit_from_runtime(obj: RuntimeObject) -> QuantitativeMethodAudit:
    """Construct a conservative audit from an actual runtime object.

    Missing scientific semantics are represented as unresolved requirements,
    never silently assumed away. In particular, a Signal has no event timestamp
    in the current contract and therefore cannot be given false temporal meaning.
    """
    identity = _runtime_identity(obj)
    provenance = _provenance(obj)
    if not provenance:
        raise ValueError("runtime object requires provenance")

    if isinstance(obj, Observation):
        method_id = f"runtime-observation:{identity}"
        question = f"Does the observed {obj.variable_id} change represent a change in the underlying phenomenon?"
        predictor_definitions = (
            obj.variable_id,
            f"denominator-status:{obj.variable_id}",
            f"coverage-process:{obj.source_id}",
            f"reporting-process:{obj.source_id}",
        )
        units = (obj.unit, "population/time", "coverage", "reporting")
        alternatives = (
            "latent phenomenon changed",
            "measurement or reporting process changed",
            "denominator or coverage changed",
        )
        temporal_requirements = (
            f"event_time={obj.event_time.isoformat()}",
            f"available_at={obj.acquisition_time.isoformat()}",
            f"publication_time={obj.publication_time.isoformat()}",
            f"revision={obj.revision}",
        )
        inference = InferenceType.DESCRIPTIVE
    elif isinstance(obj, Signal):
        method_id = f"runtime-signal:{identity}"
        question = f"Does signal {identity} contain evidence of a phenomenon change beyond observation-process and model-residual explanations?"
        predictor_definitions = (
            obj.variable_id,
            "anomaly_score",
            "trend",
            "acceleration",
            "volatility",
            "event_time:REQUIRED_FOR_TEMPORAL_INFERENCE",
        )
        units = ("runtime variable units", "probability", "variable units/time", "variable units/time^2", "variable units", "timestamp")
        alternatives = (
            "underlying phenomenon changed",
            "observation-process or measurement changed",
            "model residual or transient noise produced the signal",
        )
        temporal_requirements = (
            "signal contract currently lacks an event timestamp",
            "do not infer lead time or temporal precedence from signal identity",
        )
        inference = InferenceType.DESCRIPTIVE
    else:
        method_id = f"runtime-forecast:{identity}"
        question = f"Does forecast {identity} add out-of-sample information beyond its stated baseline and remain temporally valid?"
        predictor_definitions = (
            f"target:{obj.target}",
            f"horizon:{obj.horizon}",
            f"PIT:{obj.point_in_time_fingerprint}",
            "baseline",
            "outcome",
        )
        units = ("binary probability", "time horizon", "PIT fingerprint", "baseline probability", "binary outcome")
        alternatives = (
            "forecast contains incremental predictive information",
            "apparent performance reflects baseline prevalence/seasonality",
            "apparent performance is affected by leakage, regime change, or outcome ascertainment",
        )
        temporal_requirements = (
            f"forecast_origin={obj.origin_time.isoformat()}",
            "outcome must be after forecast origin",
            "information cutoff must not include future-derived data",
        )
        inference = InferenceType.PREDICTIVE

    return QuantitativeMethodAudit(
        method_id=method_id,
        phenomenon=question,
        scientific_question=question,
        target_population="runtime-declared population; population semantics must be verified",
        outcome_definition=obj.variable_id if isinstance(obj, (Observation, Signal)) else obj.target,
        predictor_definitions=tuple(predictor_definitions),
        units=tuple(units),
        domain="SERPIENTE runtime scientific evaluation",
        assumptions=(
            "runtime provenance identifies the represented object but does not establish real-world truth",
            "observation-process semantics remain unresolved unless explicitly represented",
            "causal effects are not authorized by this adapter",
        ),
        identification=IdentificationStatus.PARTIALLY_IDENTIFIED,
        estimation="execute the appropriate descriptive, temporal, predictive, or observation-process estimator after data eligibility is verified",
        uncertainty=(
            "measurement uncertainty",
            "observation-process uncertainty",
            "model/structural uncertainty",
        ),
        sensitivity=alternatives,
        robustness=(
            "alternative denominator specification",
            "alternative lag/temporal specification",
            "alternative baseline or model specification",
        ),
        validation=(
            "temporal holdout or point-in-time replay",
            "out-of-sample comparison against a meaningful baseline",
            "failure analysis by observation process and regime",
        ),
        benchmarks=("persistence", "historical mean", "seasonal baseline", "simple trend"),
        falsification=(
            "the leading interpretation fails if the discriminating observation supports an observation-process explanation",
            "the candidate forecast fails if a meaningful baseline performs at least as well under the predeclared metric",
        ),
        inference_type=inference,
        capability_not_authorized=(
            "causal effect",
            "prospective predictive validity",
            "operational effectiveness",
            "real-world denominator correctness",
        ),
        provenance=provenance,
        temporal_requirements=temporal_requirements,
    )


def work_from_runtime_object(obj: RuntimeObject, *, owner: str = "ESPIA") -> tuple[ScientificWork, ...]:
    """Generate deduplicated, bounded work directly from a concrete runtime object."""
    audit = quantitative_audit_from_runtime(obj)
    return work_from_quantitative_audit(audit, owner=owner)


__all__ = ["RuntimeObject", "quantitative_audit_from_runtime", "work_from_runtime_object"]
