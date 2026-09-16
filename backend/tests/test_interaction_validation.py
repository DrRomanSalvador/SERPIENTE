from datetime import datetime, timedelta, timezone

import pytest

from app.interaction_validation import InteractionSpec, PredictionRecord, compare_incremental_predictive_value

UTC = timezone.utc


def _record(origin: datetime, probability: float, *, available_offset_minutes: int = -5) -> PredictionRecord:
    return PredictionRecord(origin, origin + timedelta(minutes=available_offset_minutes), origin + timedelta(days=1), probability)


def test_interaction_adds_incremental_predictive_information_without_claiming_causality():
    spec = InteractionSpec(
        source_system="migration",
        target_system="healthcare_demand",
        direction="migration -> healthcare_demand",
        lag="1d",
        mechanism="arrival_volume_changes service demand",
        evidence_level="E3",
        causal_status="PREDICTIVE",
        measurement_dependence="PROCESS_DEPENDENT",
    )
    origins = [datetime(2026, 9, day, tzinfo=UTC) for day in (1, 2, 3, 4)]
    baseline = [_record(origin, 0.5) for origin in origins]
    interaction = [_record(origin, 0.8 if day in (1, 2) else 0.2) for day, origin in zip((1, 2, 3, 4), origins)]
    result = compare_incremental_predictive_value(spec, baseline, interaction, [1, 1, 0, 0])
    assert result.temporal_order_valid
    assert result.pit_valid
    assert result.brier_improvement > 0
    assert result.logloss_improvement > 0
    assert result.interaction_spec.causal_status == "PREDICTIVE"


def test_future_available_interaction_prediction_fails_closed():
    origin = datetime(2026, 9, 1, tzinfo=UTC)
    spec = InteractionSpec("weather", "mobility", "weather -> mobility", "6h", "weather affects travel")
    baseline = [_record(origin, 0.5)]
    interaction = [_record(origin, 0.5, available_offset_minutes=5)]
    with pytest.raises(ValueError, match="not available at its origin"):
        compare_incremental_predictive_value(spec, baseline, interaction, [1])


def test_reversed_direction_is_not_silently_equivalent():
    spec = InteractionSpec("health", "migration", "health -> migration", "7d", "health state may alter mobility")
    reverse = InteractionSpec("migration", "health", "migration -> health", "7d", "arrival volume may alter demand")
    assert spec.source_system != reverse.source_system
    assert spec.target_system != reverse.target_system


def test_pairing_requires_same_prediction_origins_and_outcome_times():
    spec = InteractionSpec("A", "B", "A -> B", "1d", "declared mechanism")
    origins = [datetime(2026, 9, day, tzinfo=UTC) for day in (1, 2, 3, 4)]
    baseline = [_record(origin, 0.5) for origin in origins]
    interaction = [_record(origin + timedelta(hours=1), 0.5) for origin in origins]
    with pytest.raises(ValueError, match="share origins"):
        compare_incremental_predictive_value(spec, baseline, interaction, [1, 1, 0, 0])
