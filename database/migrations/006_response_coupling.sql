-- Persisted warning -> decision -> action -> outcome response lineage.
-- Identity is explicit and causal interpretation remains a typed contract value.
CREATE TABLE IF NOT EXISTS serpiente_responses (
    id TEXT PRIMARY KEY,
    alert_id TEXT NOT NULL REFERENCES serpiente_alerts(id),
    decision_time TIMESTAMPTZ NOT NULL,
    action_time TIMESTAMPTZ NOT NULL,
    outcome_time TIMESTAMPTZ,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_serpiente_responses_alert_id ON serpiente_responses(alert_id);
CREATE INDEX IF NOT EXISTS idx_serpiente_responses_decision_time ON serpiente_responses(decision_time);
