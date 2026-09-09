# CEUTIA — Arquitectura del Sistema

> **Visión general de la arquitectura de CEUTIA**

---

## 🎯 Propósito

CEUTIA es un sistema de **inteligencia territorial** diseñado para:

1. **Comprender** fenómenos complejos en Ceuta (y eventualmente otros territorios)
2. **Predecir** riesgos antes de que escalen
3. **Alertar** cuando convergen múltiples indicadores de peligro
4. **Prevenir** conflictos mediante comprensión y reflexión
5. **Ayudar** a la humanidad a tomar mejores decisiones

---

## 

***

## 1. `docs/architecture/README.md` — Arquitectura General

**Crea el archivo:** `docs/architecture/README.md`

**Copia y pega esto COMPLETO:**

```markdown
# CEUTIA — Arquitectura del Sistema

> **Documentación arquitectónica completa del sistema CEUTIA**
>
> *Sistema de Inteligencia Territorial para Salvar a la Humanidad*

---

## 🎯 Propósito

Este documento describe la arquitectura completa de CEUTIA: componentes, flujos de datos, seguridad, tecnologías y decisiones clave.

---

## 🏗️ Visión General

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA PÚBLICA                              │
│  (Ciudadanía - Acceso Universal)                             │
│  -  Public Web (Next.js)                                      │
│  -  Public API (Node.js)                                      │
│  -  RAG Básico (Embeddings + Búsqueda)                        │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  CAPA OWNER / PRIVADA                        │
│  (Administrador - Acceso Restringido)                        │
│  -  Owner Web (Next.js)                                       │
│  -  Owner API (Node.js + JWT)                                 │
│  -  Epistemic Engine (Evaluación + Riesgos)                   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   CAPAS TRANSVERSALES                        │
│  -  Ingestión (Scraping + Procesamiento)                      │
│  -  IA/RAG (Embeddings + Generación)                          │
│  -  Analytics (Métricas + Alertas)                            │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   CAPA MÉDICA                                │
│  (Profesionales - Perímetro Independiente)                   │
│  -  Medical Web (Next.js)                                     │
│  -  Medical API (Node.js + Encriptación)                      │
│  -  HIPAA/GDPR Compliant                                      │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                             │
│  -  PostgreSQL + pgvector (24 tablas)                         │
│  -  Object Storage (S3/Local)                                 │
│  -  Redis (Cache + Queue)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes

### 1. Frontends

#### Public Web (`apps/public-web`)

- **Stack:** Next.js 14+, React 18, TypeScript, TailwindCSS
- **Propósito:** Interfaz pública para ciudadanía
- **Features:** Respuestas verificadas, fuentes transparentes, módulo emocional

#### Owner Web (`apps/owner-web`)

- **Stack:** Next.js 14+, React 18, TypeScript, TailwindCSS, Recharts
- **Propósito:** Panel privado para administrador/analistas
- **Features:** Radar territorial, alertas, hipótesis, escenarios, auditoría

#### Medical Web (`apps/medical-web`)

- **Stack:** Next.js 14+, React 18, TypeScript, TailwindCSS, Web Crypto API
- **Propósito:** Módulo médico independiente (HIPAA/GDPR)
- **Features:** Consultas profesionales, datos encriptados

---

### 2. Backend

#### Public API (`services/public-api`)

- **Stack:** Node.js 20+, TypeScript, Fastify, Prisma, Zod
- **Endpoints:** `/api/v1/search`, `/api/v1/answer`, `/api/v1/sources`, `/api/v1/emotional-session`, `/api/v1/medical-consultation`
- **Seguridad:** Rate limiting (100 req/min), CORS, Helmet

#### Owner API (`services/owner-api`)

- **Stack:** Node.js 20+, TypeScript, Fastify, Prisma, Zod, JWT, bcrypt
- **Endpoints:** `/api/v1/auth/login`, `/api/v1/alerts`, `/api/v1/risks`, `/api/v1/hypotheses`, `/api/v1/scenarios`, `/api/v1/sources`, `/api/v1/users`, `/api/v1/audit`
- **Seguridad:** JWT obligatorio, MFA para roles privilegiados, auditoría completa

#### Epistemic Engine (`services/epistemic-engine`)

- **Stack:** Node.js 20+, TypeScript, Python (análisis estadístico)
- **Responsabilidades:** Evaluación de evidencias, hipótesis competidoras, detección de anomalías, evaluación de riesgos, convergencias, activación de alertas
- **Algoritmos:** Bayesian inference, Z-score, Isolation Forest, Risk matrix

#### Ingestion Service (`services/ingestion`)

- **Stack:** Node.js 20+, TypeScript, Cheerio, Puppeteer, Prisma, Bull
- **Responsabilidades:** Scraping, APIs externas, procesamiento de documentos, extracción de observaciones, normalización
- **Pipeline:** Fetch → Parse → Deduplicate → Extract → Classify → Store → Notify

#### AI/RAG Service (`services/ai`)

- **Stack:** Node.js 20+, TypeScript, OpenAI API, pgvector, Prisma
- **Responsabilidades:** Embeddings, búsqueda semántica, generación de respuestas, trazabilidad
- **Pipeline RAG:** Query → Embed → Search → Rerank → Context → Generate → Cite → Return

#### Analytics Service (`services/analytics`)

- **Stack:** Node.js 20+, TypeScript, Python, Prisma, Bull
- **Responsabilidades:** Análisis de tendencias, detección de patrones, métricas por dominio, activación de alertas, notificaciones

---

### 3. Base de Datos

#### PostgreSQL + pgvector

- **Versión:** PostgreSQL 16+
- **Tablas:** 24 principales (sources, users, documents, observations, evidences, claims, hypotheses, signals, anomalies, risk_assessments, alerts, scenarios, interventions, emotional_sessions, medical_consultations, audit_log, embeddings, etc.)
- **Índices:** B-tree, GIN (arrays), HNSW (vectores), Trigram (texto)
- **Vistas:** domain_epistemic_summary, active_alerts_summary, domain_risk_summary
- **Triggers:** update_updated_at_column

---

### 4. Object Storage

- **Proveedor:** Local (dev) o S3/GCS/Azure (prod)
- **Estructura:** `storage/documents/YYYY/MM/DD/{id}.{ext}`, `storage/embeddings/`, `storage/backups/`
- **Políticas:** Retención indefinida, encriptación AES-256 (prod), backup diario

---

### 5. Cache / Queue

#### Redis

- **Uso:** Caché de respuestas, sesiones, queue (Bull)
- **Estructura:** `ceutia:cache:*`, `ceutia:session:*`, `ceutia:queue:*`
- **Políticas:** TTL 1h (caché), TTL 24h (sesiones), persistencia RDB+AOF (prod)

---

## 🔐 Seguridad

### Perímetros

```
PÚBLICO → Sin datos sensibles, rate limiting por IP
OWNER → JWT + MFA + roles + auditoría + datos sensibles
MÉDICO → Perímetro independiente + encriptación + HIPAA/GDPR
```

### Autenticación

- JWT (24h access, 7d refresh)
- MFA (TOTP) para OWNER, SENIOR_ANALYST
- bcrypt (12 rounds)

### Encriptación

- Tránsito: TLS 1.3 (prod)
- Reposo: AES-256 (documentos, medical)

### Auditoría

- Todas las acciones registradas
- Append-only, inmutable
- Retención: 365 días

---

## 📈 Escalabilidad

- **Horizontal:** Múltiples instancias, load balancer (Nginx/ALB)
- **Vertical:** PostgreSQL réplicas, más RAM/CPU
- **Cache:** Redis + CDN (Cloudflare)
- **DB:** Connection pooling (20), índices, partitioning

---

## 🛠️ Tecnologías

| Capa | Tecnología | Versión |
|---|---|---|
| Frontend | Next.js, React, TypeScript, TailwindCSS | 14+, 18+, 5+, 3+ |
| Backend | Node.js, TypeScript, Fastify, Prisma, Zod | 20+, 5+, 4+, 5+, 3+ |
| DB | PostgreSQL, pgvector, Redis | 16+, 0.5+, 7+ |
| IA | OpenAI API | GPT-4, ada-002 |
| Infra | Docker, Kubernetes, Nginx, Prometheus, Grafana | 24+, 1.28+, 1.24+, 2.45+, 10+ |

---

## 📁 Estructura de Directorios

```
ceutia-internal/
├── apps/ (public-web, owner-web, medical-web)
├── services/ (public-api, owner-api, epistemic-engine, ingestion, ai, analytics)
├── packages/ (schemas, auth, permissions, shared)
├── database/ (migrations, seeds, prisma)
├── infrastructure/ (docker, kubernetes, terraform)
├── docs/ (architecture, epistemology, domains, apis, security, deployment, operations)
├── tests/ (unit, integration, e2e)
├── config/ (.env.example)
├── .gitignore, LICENSE, README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
```

---

## 🔑 Decisiones Clave

1. **Separación Público/Owner/Médico** — Seguridad, privacidad, compliance
2. **PostgreSQL + pgvector** — Simplicidad, consistencia, coste
3. **Next.js App Router** — SSR/SSG, SEO, performance
4. **Prisma ORM** — Type safety, migrations, query builder
5. **RAG sobre Fine-tuning** — Trazabilidad, actualización fácil, menos hallucinations
6. **Auditoría Inmutable** — Trazabilidad, compliance, forensics

---

## 📚 Relacionados

- [Esquema de Base de Datos](./database-schema.md)
- [Flujo de Datos](./data-flow.md)
- [Seguridad](./security.md)

---

*Arquitectura viva. Actualizar con cada cambio significativo.*

**Última actualización:** Septiembre 2026  
**Versión:** 2.0.0
```

***

README.md

# CEUTIA
## Intelligence, Knowledge and Early-Warning Platform for Ceuta
CEUTIA is a systems-oriented intelligence and knowledge platform designed to integrate heterogeneous information, preserve its provenance, represent uncertainty and contradiction, detect emerging patterns, model competing hypotheses, and generate auditable analytical outputs.
The platform is designed around a fundamental distinction:
> Data is not knowledge.  
> Evidence is not truth.  
> A correlation is not a causal explanation.  
> A prediction is not a fact.
CEUTIA therefore treats every analytical conclusion as an epistemic object with explicit provenance, evidentiary support, uncertainty, corroboration, contradiction and temporal validity.
---
## 1. Core Objective
CEUTIA provides an architecture for studying complex and dynamically evolving systems affecting Ceuta.
The system is designed to integrate information across domains while preserving the ability to determine:
- what was observed;
- where it came from;
- when it was observed;
- how it was obtained;
- how reliable the source is;
- whether independent sources corroborate it;
- whether sources are actually independent;
- what evidence supports a claim;
- what evidence contradicts it;
- how uncertain the claim remains;
- which hypotheses explain the observations;
- how those hypotheses evolve over time;
- which indicators are changing;
- whether apparently separate events belong to a common process;
- and how analytical conclusions were produced.
CEUTIA is therefore not intended to be merely a dashboard, database, chatbot or collection of predictive models.
It is an integrated analytical system.
---
## 2. Epistemological Foundation
The fundamental unit of CEUTIA is not the document.
It is the relationship between:
```text
OBSERVATION
    ↓
SOURCE
    ↓
EVIDENCE
    ↓
CLAIM
    ↓
CORROBORATION / CONTRADICTION
    ↓
HYPOTHESIS
    ↓
MODEL
    ↓
FORECAST / SCENARIO
    ↓
ALERT
    ↓
HUMAN ASSESSMENT
    ↓
DECISION
    ↓
OUTCOME
    ↓
EVALUATION
    ↓
BELIEF REVISION

Each stage must remain distinguishable.

The system must never silently transform:

unknown → known
uncertain → certain
correlation → causation
hypothesis → fact
prediction → event
model output → reality

Any transformation between epistemic states must be explicit and auditable.

⸻

3. Design Principles

3.1 Provenance First

Every material analytical assertion should be traceable to its underlying evidence.

A user should be able to navigate from:

Alert
  → Risk Assessment
    → Hypothesis
      → Claim
        → Evidence
          → Observation
            → Source

and in the opposite direction:

Source
  → Observations
    → Evidence
      → Claims
        → Hypotheses
          → Models
            → Alerts

⸻

3.2 Uncertainty Is Data

Uncertainty is not an error condition.

It is part of the information model.

CEUTIA must distinguish, where applicable:

* aleatory uncertainty;
* epistemic uncertainty;
* measurement uncertainty;
* source uncertainty;
* model uncertainty;
* parameter uncertainty;
* structural uncertainty;
* Knightian uncertainty;
* second-order uncertainty;
* unknown unknowns.

A system that reports only a single confidence number is insufficient for high-complexity analytical environments.

⸻

3.3 Contradictions Are First-Class Objects

Conflicting evidence must not automatically be discarded or averaged away.

CEUTIA explicitly represents:

CLAIM A
    ↕
CONTRADICTION
    ↕
CLAIM B

The system must preserve:

* the conflicting observations;
* their provenance;
* their timestamps;
* their independence relationships;
* their evidentiary strength;
* their contextual validity;
* and the analytical resolution applied.

A contradiction can be informative.

⸻

3.4 Source Independence Matters

Ten articles reproducing the same original report do not necessarily constitute ten independent confirmations.

CEUTIA therefore models:

source
publication
origin
ownership
citation lineage
syndication
dependency
shared evidence

Corroboration must be weighted according to actual independence rather than simple source count.

⸻

3.5 Temporal Validity

Information changes.

A claim that was correct yesterday may be incorrect today without having been historically false.

CEUTIA therefore preserves temporal states including:

observed_at
published_at
ingested_at
effective_from
effective_until
superseded_at
verified_at
revised_at

Historical analytical states must remain reconstructable.

⸻

4. Complex-Systems Architecture

CEUTIA is designed to represent systems containing:

* nonlinear relationships;
* feedback loops;
* adaptive behaviour;
* network effects;
* contagion;
* cascading failures;
* threshold effects;
* tipping points;
* path dependence;
* emergence;
* delayed effects;
* spatial interactions;
* temporal dependencies;
* heterogeneous agents;
* endogenous responses.

The architecture must avoid assuming that:

cause → effect

is necessarily sufficient to explain system behaviour.

Where appropriate, the system should represent:

A → B
B → C
C → A

as a feedback structure.

⸻

5. Analytical Domains

The initial architecture is domain-agnostic while allowing specialized analytical modules.

Potential analytical domains include:

SOCIAL
ECONOMIC
HEALTH
EPIDEMIOLOGICAL
ENVIRONMENTAL
CLIMATE
MOBILITY
DEMOGRAPHIC
INFORMATION
MEDIA
INFRASTRUCTURE
ENERGY
WATER
TRADE
TOURISM
GOVERNANCE
PUBLIC SERVICES
SECURITY
GEOPOLITICAL

The ontology must remain extensible.

Adding a domain must not require redesigning the epistemological core.

⸻

6. Data Architecture

CEUTIA is designed to ingest heterogeneous information while maintaining separation between raw observations and derived knowledge.

Conceptually:

External Sources
       ↓
Connectors
       ↓
Ingestion
       ↓
Raw Observations
       ↓
Normalization
       ↓
Deduplication
       ↓
Entity Resolution
       ↓
Evidence Objects
       ↓
Epistemological Layer
       ↓
Knowledge Graph
       ↓
Analytical Engines
       ↓
Risk / Scenario / Forecast Layer
       ↓
Alerts and Interfaces

Raw data must not be silently overwritten by normalized or interpreted data.

Original evidence should remain recoverable according to retention, legal and governance requirements.

⸻

7. Knowledge Graph

CEUTIA is designed to represent entities and relationships as a dynamic knowledge graph.

Conceptual entities include:

PERSON
ORGANIZATION
INSTITUTION
LOCATION
EVENT
ASSET
INFRASTRUCTURE
INDICATOR
SOURCE
OBSERVATION
EVIDENCE
CLAIM
HYPOTHESIS
MODEL
SCENARIO
ALERT
INTERVENTION
OUTCOME

Relationships may include:

LOCATED_IN
AFFECTS
ASSOCIATED_WITH
CAUSES
INFLUENCES
PRECEDES
FOLLOWS
CORROBORATES
CONTRADICTS
DERIVED_FROM
SUPPORTED_BY
REFUTES
DEPENDS_ON
PART_OF
SIMILAR_TO

Relationships themselves may require provenance and uncertainty.

The graph must therefore be capable of representing uncertainty about relationships, not only uncertainty about nodes.

⸻

8. Analytical Engines

CEUTIA is designed to support multiple analytical approaches rather than a single predictive model.

Potential analytical components include:

Statistical analysis

* descriptive statistics;
* time-series analysis;
* Bayesian inference;
* hierarchical models;
* survival analysis;
* spatial statistics.

Anomaly detection

* robust statistical detection;
* Mahalanobis distance;
* isolation-based methods;
* autoencoders;
* multivariate anomaly detection;
* change-point detection;
* regime-shift detection.

Network analysis

* centrality;
* community detection;
* temporal networks;
* influence propagation;
* diffusion;
* cascade analysis;
* contagion models.

Complex-systems analysis

* nonlinear dynamics;
* feedback analysis;
* tipping-point detection;
* agent-based models;
* adaptive-system modelling;
* sensitivity analysis.

Predictive modelling

Models may be used for:

forecasting
classification
risk estimation
scenario generation
anomaly prioritization
resource planning
early-warning systems

No model output should automatically become a factual claim.

⸻

9. Competing Hypotheses

CEUTIA must support multiple simultaneously active explanations.

Conceptually:

Observation Set
      ↓
┌───────────────┐
│ Hypothesis A  │
├───────────────┤
│ Hypothesis B  │
├───────────────┤
│ Hypothesis C  │
├───────────────┤
│ Null / Base   │
└───────────────┘
      ↓
Evidence Update
      ↓
Relative Support
      ↓
Uncertainty
      ↓
Revision

The system must not optimize exclusively for one preferred explanation.

A null hypothesis, baseline explanation or status-quo explanation should be representable where analytically appropriate.

⸻

10. Risk and Early Warning

CEUTIA is designed to detect changes in system state before they necessarily become obvious through conventional indicators.

The early-warning architecture may combine:

baseline deviation
+
velocity
+
acceleration
+
spatial concentration
+
network connectivity
+
cross-domain coupling
+
historical analogues
+
threshold proximity
+
model forecasts
+
uncertainty

A warning should contain enough information to answer:

What changed?
Compared with what baseline?
When did it change?
Where did it change?
How unusual is it?
Which independent observations support it?
What contradicts it?
Which mechanisms could explain it?
How uncertain is the assessment?
What could happen next?
What would falsify the assessment?

⸻

11. Scenario Engine

CEUTIA should distinguish prediction from scenario analysis.

A prediction asks:

What is most likely to happen?

A scenario asks:

What could happen under a defined set of conditions?

The scenario engine should support:

* baseline scenarios;
* adverse scenarios;
* favorable scenarios;
* stress scenarios;
* counterfactual scenarios;
* cascading scenarios;
* intervention scenarios.

Scenario outputs must retain assumptions and parameterizations.

⸻

12. Counterfactual Reasoning

Where supported by the underlying model, CEUTIA may evaluate questions such as:

What changes if X does not occur?
What changes if X increases?
What changes if intervention Y is introduced?
Which downstream variables are most sensitive?

Counterfactual outputs must be explicitly labelled as model-dependent.

They must never be represented as observations.

⸻

13. Human-in-the-Loop Governance

CEUTIA is designed as an analytical decision-support system.

Human experts remain responsible for interpreting high-impact analytical outputs.

The system should distinguish:

AUTOMATED OBSERVATION
AUTOMATED ANALYSIS
AUTOMATED ALERT
HUMAN REVIEW
HUMAN ASSESSMENT
HUMAN DECISION

The system must preserve who or what generated each material analytical transition.

⸻

14. Auditability

Material analytical operations should be reconstructable.

An auditor should be able to determine:

what happened
when it happened
who or what performed it
which data was involved
which model version was used
which configuration was active
which evidence supported the output
which uncertainty existed
which subsequent correction occurred

The system should support reproducibility of historical analytical states wherever technically and legally feasible.

⸻

15. Security Model

Security is not limited to infrastructure protection.

CEUTIA treats the following as security properties:

confidentiality
integrity
availability
authenticity
provenance integrity
epistemic integrity
model integrity
configuration integrity
audit integrity
identity integrity
authorization integrity

A compromised source can contaminate evidence.

Contaminated evidence can produce an incorrect claim.

An incorrect claim can alter a model.

An altered model can generate a false alert.

A false alert can influence a human decision.

Therefore:

SOURCE SECURITY
      ↓
EVIDENCE INTEGRITY
      ↓
KNOWLEDGE INTEGRITY
      ↓
MODEL INTEGRITY
      ↓
ANALYTICAL INTEGRITY
      ↓
DECISION INTEGRITY

This chain is a core security consideration.

⸻

16. Public / Owner Separation

The architecture must maintain strict logical separation between publicly accessible information and owner-controlled information.

Conceptually:

                    CEUTIA
                      │
             ┌────────┴────────┐
             │                 │
          PUBLIC             OWNER
             │                 │
      Public Outputs     Restricted Analysis
             │                 │
       Public Data       Private / Restricted Data

Public interfaces must never gain access to owner-restricted data merely because both systems use the same underlying infrastructure.

Authorization must be enforced server-side.

Client-side hiding is not an isolation mechanism.

⸻

17. Privacy

CEUTIA must apply privacy-by-design principles.

Where personal data is processed, the architecture should support:

data minimization
purpose limitation
access control
retention controls
auditability
pseudonymization where appropriate
deletion mechanisms where legally applicable
data-subject rights workflows where applicable

Special-category data requires additional legal and technical controls.

The system must not collect personal data merely because it is technically possible to do so.

⸻

18. AI Governance

AI models must be treated as components with lifecycle state.

A model should have:

model_id
version
training_data_reference
training_period
features
architecture
parameters
evaluation_metrics
limitations
known_failure_modes
deployment_status
approval_status
provenance

Model outputs must remain linked to the exact model version that generated them.

A model update must not silently alter historical analytical conclusions.

⸻

19. Model Evaluation

CEUTIA should evaluate models using more than aggregate accuracy.

Depending on the task, evaluation may include:

precision
recall
F1
ROC-AUC
PR-AUC
calibration
Brier score
false-positive rate
false-negative rate
lead time
stability
drift
robustness
sensitivity
specificity
out-of-sample performance
backtesting

For early-warning systems, lead time and false-alarm characteristics are particularly important.

A model that predicts everything as high risk is not necessarily useful.

⸻

20. Concept Drift

The system must assume that relationships can change.

Examples include:

population changes
policy changes
economic regime changes
media ecosystem changes
technological changes
climate changes
behavioural adaptation
institutional adaptation

Consequently, model validity must be monitored over time.

Historical performance does not guarantee future performance.

⸻

21. Feedback Effects

Analytical systems can change the systems they observe.

If an alert changes behaviour, and behaviour changes the measured variables, the analytical system becomes part of the feedback loop.

CEUTIA should therefore support analysis of:

observation
→ intervention
→ behavioural response
→ new observation

This is essential when evaluating interventions and early-warning systems.

⸻

22. Information Integrity

CEUTIA must distinguish between:

authentic information
accurate information
independently corroborated information
contextually valid information
temporally valid information

Authenticity alone does not imply truth.

Multiple sources alone do not imply independence.

A high-confidence model output does not imply factual certainty.

These distinctions must remain explicit in the data model.

⸻

23. Failure Philosophy

CEUTIA is designed under the assumption that:

sources can fail
sensors can fail
APIs can fail
models can fail
data can be missing
data can be corrupted
labels can be wrong
assumptions can be wrong
analysts can be wrong

The architecture should therefore favour:

graceful degradation
explicit uncertainty
fail-closed authorization
observability
reproducibility
rollback
versioning
auditability
human review

over silent failure.

⸻

24. No Single Point of Epistemic Failure

The system should avoid allowing one:

source
model
indicator
algorithm
analyst
dataset

to determine a high-impact conclusion without appropriate corroboration or explicit justification.

Analytical independence is a system property, not merely a source property.

⸻

25. Reproducibility

Analytical outputs should be reproducible whenever possible.

Reproduction requires preserving, where applicable:

input data references
source versions
processing versions
code version
model version
configuration
parameters
random seeds
timestamps
environment metadata

The objective is not merely to reproduce the final number.

It is to reconstruct the analytical pathway that generated it.

⸻

26. Observability

CEUTIA should expose operational telemetry covering:

system health
ingestion latency
ingestion failures
queue depth
processing latency
API latency
database health
resource utilization
model execution
model failures
security events
data-quality anomalies
epistemic anomalies

Operational observability and analytical observability should remain distinguishable.

A system can be operationally healthy while producing analytically defective results.

⸻

27. Data Quality

Data quality should be assessed independently from source reputation.

Relevant dimensions include:

completeness
timeliness
accuracy
consistency
uniqueness
validity
granularity
coverage
missingness
measurement error
provenance

Quality assessments should be versioned because source quality can change over time.

⸻

28. Early-Warning Integrity

An early-warning signal should never be interpreted solely from its magnitude.

The system should consider, where available:

baseline
trend
rate of change
variance
seasonality
structural breaks
spatial distribution
network position
cross-domain agreement
source independence
historical analogues
model uncertainty
contradictory evidence

The objective is to distinguish:

noise
anomaly
transient disturbance
structural change
emerging process
systemic transition

⸻

29. Architecture Evolution

CEUTIA is intended to evolve incrementally.

The initial implementation should prioritize:

epistemological integrity
data provenance
security
auditability
modularity
testability
observability

before adding increasingly complex predictive capabilities.

Complexity must be earned by evidence.

A sophisticated model attached to poor data and weak provenance produces sophisticated error.

⸻

30. Repository Structure

The repository is organized into distinct architectural layers.

ceutia/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── epistemology/
│   │   ├── analytics/
│   │   ├── ingestion/
│   │   ├── ontology/
│   │   ├── security/
│   │   ├── governance/
│   │   └── api/
│   └── tests/
│
├── ontology/
│
├── governance/
│
├── infrastructure/
│
├── docs/
│
├── scripts/
│
└── README.md

Each layer should have a clearly defined responsibility.

Cross-layer dependencies should be deliberate and testable.

⸻

31. Development Philosophy

CEUTIA should be developed as an engineered analytical system rather than as a collection of scripts.

Every major capability should have:

contract
implementation
validation
tests
observability
documentation
security controls
failure handling

No critical component should depend on undocumented behaviour.

⸻

32. Analytical Output Contract

A mature CEUTIA analytical output should be capable of expressing at minimum:

WHAT
WHEN
WHERE
WHY IT MATTERS
EVIDENCE
SOURCE
PROVENANCE
CORROBORATION
CONTRADICTION
UNCERTAINTY
CONFIDENCE
ALTERNATIVE EXPLANATIONS
BASELINE
MODEL
MODEL VERSION
ASSUMPTIONS
FORECAST
SCENARIOS
FALSIFICATION CONDITIONS
LIMITATIONS

The objective is not to produce outputs that merely sound convincing.

The objective is to produce outputs whose reasoning can be inspected.

⸻

33. Fundamental Invariant

CEUTIA must preserve the distinction between:

REALITY
    ↓
OBSERVATION
    ↓
DATA
    ↓
EVIDENCE
    ↓
CLAIM
    ↓
HYPOTHESIS
    ↓
MODEL
    ↓
FORECAST
    ↓
DECISION

The system may infer across these layers.

It must never silently collapse them.

⸻

34. Long-Term Objective

The long-term architecture is intended to support a continuously evolving analytical environment in which:

new information
      ↓
updates evidence
      ↓
changes claim support
      ↓
changes hypothesis weights
      ↓
changes model state
      ↓
changes risk estimates
      ↓
changes scenarios
      ↓
changes alerts
      ↓
produces actions
      ↓
produces outcomes
      ↓
generates new evidence
      ↓
updates the system

CEUTIA therefore operates conceptually as a closed analytical learning loop.

Its objective is not certainty.

Its objective is to improve the quality, traceability, timeliness and calibration of understanding under uncertainty.

⸻

35. Current Status

CEUTIA is under active development.

Architectural claims must be distinguished from implemented capabilities.

The repository should never represent a planned control, certification, integration, model, security property or analytical capability as operational until it has been implemented and verified.

Implementation status should therefore be treated explicitly as:

PLANNED
DESIGNED
IMPLEMENTED
TESTED
VERIFIED
OPERATIONAL
DEPRECATED

Only evidence should promote a capability from one state to another.

⸻

36. Engineering Rule

The central engineering rule of CEUTIA is:

Never hide uncertainty that materially changes the interpretation of an observation, claim, model, forecast or decision.

CEUTIA
Intelligence
Knowledge
Evidence
Uncertainty
Systems