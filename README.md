# SERPIENTE

SERPIENTE is the executable longitudinal risk-signal and early-warning runtime for CeutIA.

The system separates evidence, temporal information, prediction, uncertainty and causal interpretation. It is designed for complex territorial monitoring, but execution quality is not treated as proof of predictive effectiveness.

## Executable chain

```text
REAL SOURCE
  -> INGESTION
  -> SEMANTIC MAPPING
  -> POINT-IN-TIME VALIDATION
  -> PROVENANCE
  -> OBSERVATION HISTORY
  -> LONGITUDINAL STATE
  -> EVENT
  -> SIGNAL
  -> PATTERN
  -> TRAJECTORY
  -> RISK / ALERT
  -> FORECAST
  -> UNCERTAINTY
  -> PROSPECTIVE OUTCOME
  -> VALIDATION FEEDBACK
```

The runtime implements:

- adapter-based JSON/CSV/HTTPS ingestion;
- official-source allowlisting and SSRF protection;
- source, dataset, variable, semantic definition, unit, geography, event time, publication time, acquisition time, version, revision, provenance, quality and transformation lineage;
- point-in-time replay and revision-aware history;
- lagged predictors, rolling trend, acceleration, volatility and cross-variable interactions;
- explicit regime/change screening;
- event, signal, pattern, trajectory, propagation and cascade objects;
- data-process-change detection to prevent false high-confidence alerts;
- temporal train/calibration/test separation;
- calibrated logistic forecasting and gradient-boosting model disagreement;
- prevalence and seasonal baselines;
- multi-horizon models;
- aleatoric, epistemic, measurement, parameter and structural uncertainty fields;
- prospective outcome capture and forecast-error feedback;
- authenticated RBAC-protected API;
- request-size and rate controls;
- transactional SQLite persistence with restart-safe schema evolution;
- containerized execution and CI validation.

## Scientific boundary

SERPIENTE distinguishes:

```text
association
    != temporal dependence
    != prediction
    != causal hypothesis
    != causal inference
    != intervention effect
```

A forecast is never interpreted as a causal effect. Model agreement is not treated as truth. Missing data are not converted to zero. Non-finite values are rejected. Future information and post-outcome variables are rejected from the forecasting pathway.

The implemented validation protocol contains chronological holdout, calibration, out-of-sample scoring, baseline comparison, model comparison, numerical adversarial checks, temporal leakage checks, revision leakage checks and distribution-drift testing.

## CeutIA boundary

CeutIA accepts a versioned prediction envelope containing:

- prediction identity;
- origin time and horizon;
- target;
- probability and interval;
- uncertainty components;
- model disagreement;
- regime;
- provenance;
- point-in-time fingerprint;
- alert identifiers.

CeutIA validates that the prediction was available at decision time and incorporates its identity and provenance into the final epistemic decision contract and audit chain. Future predictions are rejected.

## Official-source configuration

`config/official_sources.yaml` currently registers official-source boundaries for AEMET OpenData and INE JSON services. Credentials are external to the repository. A source cannot be activated without its required credentials and an explicit semantic mapping.

Adding a source does not require changing the predictive core. The source must instead provide an adapter/mapper satisfying the canonical observation contract.

## Running

Install the package and development dependencies:

```bash
python -m pip install -e '.[dev]'
pytest -q backend/tests
```

Run the API locally:

```bash
SERPIENTE_API_KEYS_JSON='{"analyst-key":"ANALYST"}' serpiente
```

The default local bind is `127.0.0.1:8001`. Network exposure must be explicit through `SERPIENTE_HOST`.

Container execution is provided by `Dockerfile` and `docker-compose.yml`.

## API

`GET /health` — process liveness.

`GET /ready` — runtime persistence readiness.

`POST /v1/observations` — authenticated observation ingestion; requires `INGESTOR`, `ANALYST` or `ADMIN`.

`POST /v1/process` — authenticated event-to-alert processing; requires `ANALYST` or `ADMIN`.

`POST /v1/outcomes` — authenticated prospective forecast outcome capture; requires `ANALYST` or `ADMIN` and a previously persisted prediction.

## Empirical status

The repository contains engineering and prospective-validation infrastructure. It does not contain sufficient real-world prospective observations to establish predictive effectiveness, calibration in deployment, intervention effectiveness or causal benefit.

Those properties must be estimated from precommitted prospective evaluation after deployment. Historical reconstruction and successful software execution are not substitutes for prospective validation.

## Repository role

SERPIENTE is the mathematical and longitudinal signal layer. CeutIA is the evidence, epistemic and decision-intelligence layer. The executable boundary preserves provenance, temporal semantics, uncertainty and the distinction between prediction and causation.
