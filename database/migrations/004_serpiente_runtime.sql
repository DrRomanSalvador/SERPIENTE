-- SERPIENTE executable runtime persistence layer.
-- Payloads retain the canonical Python contract while temporal columns remain queryable.

CREATE TABLE IF NOT EXISTS serpiente_observations (
    id TEXT PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    publication_time TIMESTAMPTZ NOT NULL,
    acquisition_time TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_serpiente_observations_event_time ON serpiente_observations(event_time);
CREATE INDEX IF NOT EXISTS idx_serpiente_observations_acquisition_time ON serpiente_observations(acquisition_time);

CREATE TABLE IF NOT EXISTS serpiente_events (
    id TEXT PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_serpiente_events_event_time ON serpiente_events(event_time);

CREATE TABLE IF NOT EXISTS serpiente_signals (
    id TEXT PRIMARY KEY,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS serpiente_forecasts (
    id TEXT PRIMARY KEY,
    origin_time TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_serpiente_forecasts_origin_time ON serpiente_forecasts(origin_time);

CREATE TABLE IF NOT EXISTS serpiente_alerts (
    id TEXT PRIMARY KEY,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS serpiente_outcomes (
    id BIGSERIAL PRIMARY KEY,
    prediction_id TEXT NOT NULL REFERENCES serpiente_forecasts(id),
    outcome_time TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_serpiente_outcomes_prediction_id ON serpiente_outcomes(prediction_id);
