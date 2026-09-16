# SERPIENTE — Verified Implementation Boundary

As of 2026-09-16, the repository contains an executable Python runtime package, PostgreSQL persistence, authenticated API endpoints, temporal validation, forecasting, and runtime integration tests. The earlier statement that no executable runtime package was present is obsolete and must not be used as current engineering evidence.

Verified implementation areas include:

- Observation ingestion with timezone-aware event/publication/acquisition semantics and provenance.
- Event → signal → pattern → trajectory → alert runtime processing.
- Temporal forecasting with ordered train/calibration/test partitions and explicit binary-target validation.
- PostgreSQL runtime persistence for observations, events, signals, forecasts, alerts and outcomes.
- Durable forecast-outcome foreign-key enforcement and one-outcome-per-forecast uniqueness.
- Idempotent identical outcome retries and rejection of conflicting outcome retries at the PostgreSQL runtime boundary.
- Authenticated API roles, request-size/rate controls and readiness/liveness endpoints.
- Runtime compilation, general tests, PostgreSQL integration, security checks, dependency audit, Compose validation and image build are covered by CI workflows.

Engineering boundaries that remain explicit:

- The SERPIENTE point-in-time fingerprint carried by `Forecast` identifies a declared PIT state, but v1.1 does not yet cryptographically bind the actual feature matrix `X_t` to a reconstructible PIT manifest and derivation identity. This is a scientific/engineering handoff and is not claimed closed by the runtime tests.
- Forecast uncertainty components are bounded and finite but remain heuristic uncertainty constructions; this is not evidence of calibrated predictive uncertainty.
- Temporal holdout prevents the tested classes of target/outcome leakage, but arbitrary future-derived feature leakage cannot be proven from timestamps alone without feature-lineage enforcement.
- Calibration and historical out-of-sample performance are not prospective effectiveness evidence.
- Cross-repository CeutIA compatibility is verified on the CeutIA canonical contract/transport path; the legacy `ceutia_boundary.py` envelope is not the canonical v1.1 contract and must not be treated as an alternative production transport.

No predictive effectiveness, causal validity, or prospective scientific validity claim is made from repository implementation or CI evidence alone.
