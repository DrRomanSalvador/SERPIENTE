-- A forecast has one canonical evaluated outcome. This prevents duplicate
-- outcome rows across concurrent application instances and makes retries
-- deterministic at the database boundary.
CREATE UNIQUE INDEX IF NOT EXISTS uq_serpiente_outcomes_prediction_id
    ON serpiente_outcomes(prediction_id);
