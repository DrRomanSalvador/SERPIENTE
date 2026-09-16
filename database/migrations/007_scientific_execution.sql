CREATE TABLE IF NOT EXISTS serpiente_scientific_work (
    id TEXT PRIMARY KEY,
    fingerprint JSONB NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS serpiente_scientific_results (
    id TEXT PRIMARY KEY,
    work_id TEXT NOT NULL REFERENCES serpiente_scientific_work(id),
    runtime_id TEXT NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS serpiente_scientific_claims (
    id TEXT PRIMARY KEY,
    payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scientific_results_runtime_id
    ON serpiente_scientific_results(runtime_id);
