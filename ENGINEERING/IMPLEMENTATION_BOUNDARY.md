# SERPIENTE — Verified Implementation Boundary

As of 2026-09-14, the repository contains architecture/design documentation and a PostgreSQL schema/seed layer, but no executable SERPIENTE runtime package is present in the repository tree.

Verified engineering state:

- `database/migrations/*.sql` executes successfully against a clean PostgreSQL 17 + pgvector instance.
- `database/seeds/001_initial_data.sql` executes successfully after the canonical schema.
- UUID-array relationships are protected by explicit PostgreSQL validation triggers.
- The bootstrap owner account is disabled until real credentials and MFA are provisioned.
- `.github/workflows/database-validation.yml` continuously verifies clean installation, seed execution, extensions, relations, and an invalid-reference failure path.

Not verified because the implementation is absent:

- SERPIENTE event ingestion runtime.
- Event → signal → pattern → trajectory → alert execution.
- Real-time source adapters.
- Mathematical risk-signal computation.
- Calibration, temporal out-of-sample validation and prospective effectiveness.
- Runtime API/service execution.
- Cross-repository CeutIA ↔ SERPIENTE executable integration.

The absence of executable runtime code is treated as an implementation boundary, not as evidence of predictive capability. No predictive effectiveness claim is made from the database or architecture layer alone.
