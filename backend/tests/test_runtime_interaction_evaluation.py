from datetime import datetime, timedelta, timezone

from app.interaction_validation import InteractionSpec, PredictionRecord
from app.runtime import SerpienteRuntime

UTC = timezone.utc


def test_runtime_exposes_interaction_evaluation_without_causal_upgrade():
    runtime = SerpienteRuntime()
    spec = InteractionSpec("A", "B", "A -> B", "1d", "declared mechanism", evidence_level="E2", causal_status="PREDICTIVE")
    origins = [datetime(2026, 9, d, tzinfo=UTC) for d in (1, 2)]
    baseline = tuple(PredictionRecord(o, o - timedelta(minutes=5), o + timedelta(days=1), 0.5) for o in origins)
    interaction = tuple(PredictionRecord(o, o - timedelta(minutes=5), o + timedelta(days=1), p) for o, p in zip(origins, (0.9, 0.1)))
    result = runtime.evaluate_interaction(spec, baseline, interaction, (1, 0))
    assert result.pit_valid
    assert result.brier_improvement > 0
    assert result.interaction_spec.causal_status == "PREDICTIVE"
