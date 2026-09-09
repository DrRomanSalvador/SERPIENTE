Perfecto. Vamos a hacer el siguiente archivo **realmente brillante**.

***

## `docs/architecture/database-schema.md` — Esquema de Base de Datos Detallado

**Crea el archivo:** `docs/architecture/database-schema.md`

**Copia y pega esto:**

```markdown
# CEUTIA — Esquema de Base de Datos Detallado

> **Documentación exhaustiva del esquema de base de datos PostgreSQL + pgvector**
>
> *24 tablas principales, 10 dominios, auditoría inmutable, embeddings vectoriales*

---

## 🎯 Propósito

Este documento describe **cada tabla, columna, índice, relación y trigger** del esquema de CEUTIA.

**Características clave:**

- ✅ **24 tablas principales** — Fuentes, usuarios, documentos, observaciones, evidencias, afirmaciones, hipótesis, señales, anomalías, riesgos, alertas, escenarios, intervenciones, sesiones emocionales, consultas médicas, auditoría, embeddings, configuración, relaciones
- ✅ **10 dominios** — Biológico/sanitario, ambiental/climático, violencia/escalada, polarización sociológica, desinformación, influencia/propaganda, fronterizo/geopolítico, territorial/integrado, infraestructuras/servicios, económico/social
- ✅ **Auditoría inmutable** — Append-only, WORM (Write Once Read Many)
- ✅ **Embeddings vectoriales** — pgvector (HNSW index) para búsqueda semántica
- ✅ **Grafo de conocimiento** — entity_relationships para trazabilidad epistemológica

---

## 📊 Diagrama Entidad-Relación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FUENTES Y DOCUMENTOS                                 │
│                                                                              │
│  ┌──────────┐     ┌───────────┐     ┌──────────────┐                        │
│  │ sources  │────▶│ documents │────▶│ observations │                        │
│  │ (30+)    │     │           │     │              │                        │
│  └──────────┘     └───────────┘     └──────────────┘                        │
│                        │                    │                                │
│                        │                    ▼                                │
│                        │             ┌───────────┐                          │
│                        │             │ evidences │                          │
│                        │             └───────────┘                          │
│                        │                    │                                │
└────────────────────────┼────────────────────┼────────────────────────────────┘
                         │                    │
                         ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NÚCLEO EPISTEMOLÓGICO                                │
│                                                                              │
│  ┌───────────┐     ┌────────────┐     ┌────────────┐                        │
│  │  claims   │────▶│ hypotheses │────▶│ competing  │                        │
│  │           │     │            │     │ hypotheses │                        │
│  └───────────┘     └────────────┘     └────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SEÑALES Y ANOMALÍAS                                  │
│                                                                              │
│  ┌──────────┐     ┌───────────┐     ┌──────────────────┐                    │
│  │ signals  │────▶│ anomalies │────▶│ risk_assessments │                    │
│  │          │     │           │     │                  │                    │
│  └──────────┘     └───────────┘     └──────────────────┘                    │
│                                            │                                 │
│                                            ▼                                 │
│                                     ┌──────────────────┐                    │
│                                     │risk_convergences │                    │
│                                     └──────────────────┘                    │
│                                            │                                 │
└────────────────────────────────────────────┼─────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ALERTAS Y ESCENARIOS                                 │
│                                                                              │
│  ┌───────────┐     ┌────────────┐     ┌──────────────┐                      │
│  │  alerts   │────▶│ scenarios  │────▶│interventions │                      │
│  │           │     │            │     │              │                      │
│  └───────────┘     └────────────┘     └──────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAPA MÉDICA (INDEPENDIENTE)                          │
│                                                                              │
│  ┌────────────────────┐     ┌──────────────────────┐                        │
│  │emotional_sessions  │     │medical_consultations │                        │
│  │                    │     │                      │                        │
│  └────────────────────┘     └──────────────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         INFRAESTRUCTURA                                      │
│                                                                              │
│  ┌──────────┐     ┌───────────┐     ┌──────────────────┐                    │
│  │  users   │────▶│   roles   │     │  audit_log       │                    │
│  │          │     │           │     │  (inmutable)     │                    │
│  └──────────┘     └───────────┘     └──────────────────┘                    │
│                                                                              │
│  ┌──────────┐     ┌───────────┐     ┌──────────────────┐                    │
│  │embeddings│     │system_cfg │     │entity_relationships│                  │
│  │(pgvector)│     │domain_cfg │     │  (grafo)         │                    │
│  └──────────┘     └───────────┘     └──────────────────┘                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Tablas Detalladas

### 1. `sources` — Fuentes Autorizadas

**Propósito:** Registrar fuentes de información autorizadas (gubernamentales, académicas, medios, etc.)

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `name` | VARCHAR(500) | NO | - | Nombre de la fuente (único) |
| `description` | TEXT | SÍ | - | Descripción de la fuente |
| `type` | source_type | NO | - | Tipo (GOVERNMENT_OFFICIAL, NEWS_MEDIA, etc.) |
| `quality` | source_quality | NO | UNVERIFIED | Calidad (VERIFIED_HIGH, VERIFIED_MEDIUM, etc.) |
| `independence` | source_independence | NO | UNKNOWN | Independencia (PRIMARY, SECONDARY_INDEPENDENT, etc.) |
| `url` | VARCHAR(2048) | SÍ | - | URL de la fuente |
| `official_name` | VARCHAR(500) | SÍ | - | Nombre oficial (si es gubernamental) |
| `country` | VARCHAR(100) | SÍ | - | País de origen |
| `region` | VARCHAR(100) | SÍ | - | Región (ej: Andalucía, Ceuta) |
| `language` | VARCHAR(10) | SÍ | - | Idioma (es, en, fr, etc.) |
| `first_seen_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se registró la fuente |
| `last_verified_at` | TIMESTAMPTZ | SÍ | - | Cuándo se verificó por última vez |
| `verified_by` | UUID | SÍ | - | Usuario que verificó (references users) |
| `domains` | analysis_domain[] | SÍ | - | Dominios que cubre (array de enums) |
| `tags` | TEXT[] | SÍ | - | Tags para clasificación |
| `is_active` | BOOLEAN | NO | true | Si está activa |
| `is_blocked` | BOOLEAN | NO | false | Si está bloqueada (desinformación, etc.) |
| `blocked_reason` | TEXT | SÍ | - | Razón del bloqueo |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `updated_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se actualizó |
| `created_by` | UUID | SÍ | - | Usuario que creó (references users) |

**Índices:**

```sql
CREATE INDEX idx_sources_type ON sources(type);
CREATE INDEX idx_sources_quality ON sources(quality);
CREATE INDEX idx_sources_domains ON sources USING GIN(domains);
CREATE INDEX idx_sources_tags ON sources USING GIN(tags);
CREATE INDEX idx_sources_active ON sources(is_active);
CREATE INDEX idx_sources_name_trgm ON sources USING GIN(name gin_trgm_ops);
```

**Constraints:**

```sql
ALTER TABLE sources ADD CONSTRAINT sources_name_unique UNIQUE (name);
ALTER TABLE sources ADD CONSTRAINT sources_url_unique UNIQUE (url);
```

**Ejemplo:**

```sql
INSERT INTO sources (name, type, quality, independence, description, domains)
VALUES (
  'Ministerio del Interior',
  'GOVERNMENT_OFFICIAL',
  'VERIFIED_HIGH',
  'PRIMARY',
  'Ministerio del Interior de España',
  ARRAY['VIOLENCE_ESCALATION', 'BORDER_GEOPOLITICAL']
);
```

---

### 2. `users` — Usuarios del Sistema

**Propósito:** Registrar usuarios ( Owner, analistas, profesionales médicos, ciudadanos)

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `email` | VARCHAR(255) | NO | - | Email (único) |
| `username` | VARCHAR(100) | NO | - | Username (único) |
| `password_hash` | VARCHAR(255) | NO | - | Hash de contraseña (Argon2id) |
| `mfa_enabled` | BOOLEAN | NO | false | Si tiene MFA habilitado |
| `mfa_secret` | VARCHAR(255) | SÍ | - | Secret TOTP (encriptado) |
| `full_name` | VARCHAR(255) | SÍ | - | Nombre completo |
| `role` | VARCHAR(100) | NO | CITIZEN | Rol principal (OWNER, ANALYST, etc.) |
| `organization` | VARCHAR(255) | SÍ | - | Organización (si aplica) |
| `is_active` | BOOLEAN | NO | true | Si está activo |
| `is_verified` | BOOLEAN | NO | false | Si email verificado |
| `last_login_at` | TIMESTAMPTZ | SÍ | - | Último login |
| `failed_login_attempts` | INTEGER | NO | 0 | Intentos fallidos |
| `locked_until` | TIMESTAMPTZ | SÍ | - | Bloqueado hasta (brute force) |
| `password_changed_at` | TIMESTAMPTZ | NO | NOW() | Cuándo cambió password |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `updated_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se actualizó |

**Índices:**

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
```

**Constraints:**

```sql
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT users_username_unique UNIQUE (username);
```

---

### 3. `roles` — Roles y Permisos

**Propósito:** Definir roles con permisos granulares

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `name` | VARCHAR(100) | NO | - | Nombre del rol (único) |
| `description` | TEXT | SÍ | - | Descripción |
| `permissions` | JSONB | NO | '{}' | Permisos ({"alerts": ["read", "write"], ...}) |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |

**Ejemplo de permissions JSONB:**

```json
{
  "alerts": ["read", "write", "delete"],
  "risks": ["read", "write"],
  "hypotheses": ["read"],
  "users": ["read"],
  "config": ["read"],
  "audit": ["read"]
}
```

---

### 4. `user_roles` — Asignación de Roles a Usuarios

**Propósito:** Asignar múltiples roles a usuarios (muchos-a-muchos)

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `user_id` | UUID | NO | - | Usuario (references users) |
| `role_id` | UUID | NO | - | Rol (references roles) |
| `granted_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se concedió |
| `granted_by` | UUID | SÍ | - | Quién concedió (references users) |
| `expires_at` | TIMESTAMPTZ | SÍ | - | Expiración (si es temporal) |

**Primary Key:**

```sql
ALTER TABLE user_roles ADD PRIMARY KEY (user_id, role_id);
```

---

### 5. `documents` — Documentos

**Propósito:** Almacenar documentos con procedencia y estado epistemológico

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `title` | VARCHAR(500) | NO | - | Título |
| `description` | TEXT | SÍ | - | Descripción |
| `type` | document_type | NO | - | Tipo (OFFICIAL_REPORT, NEWS_ARTICLE, etc.) |
| `content_hash` | VARCHAR(64) | NO | - | SHA-256 del contenido (único) |
| `content_type` | VARCHAR(100) | SÍ | - | MIME type (application/pdf, text/html, etc.) |
| `content_size_bytes` | BIGINT | SÍ | - | Tamaño en bytes |
| `language` | VARCHAR(10) | SÍ | - | Idioma (es, en, fr) |
| `source_id` | UUID | NO | - | Fuente (references sources) |
| `original_url` | VARCHAR(2048) | SÍ | - | URL original |
| `published_at` | TIMESTAMPTZ | SÍ | - | Cuándo se publicó |
| `retrieved_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se recuperó |
| `domains` | analysis_domain[] | SÍ | - | Dominios que cubre |
| `epistemic_state` | epistemic_state | NO | DECLARATION | Estado epistemológico |
| `confidence_score` | DECIMAL(5,4) | SÍ | - | Confianza (0-1) |
| `storage_provider` | VARCHAR(50) | SÍ | - | Provider (local, s3, gcs) |
| `storage_bucket` | VARCHAR(255) | SÍ | - | Bucket |
| `storage_key` | VARCHAR(500) | SÍ | - | Key/path |
| `storage_url` | VARCHAR(2048) | SÍ | - | URL de descarga |
| `processing_status` | VARCHAR(50) | NO | PENDING | Estado de procesamiento |
| `processed_at` | TIMESTAMPTZ | SÍ | - | Cuándo se procesó |
| `processing_error` | TEXT | SÍ | - | Error si falló |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `updated_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se actualizó |
| `created_by` | UUID | SÍ | - | Usuario que creó |

**Índices:**

```sql
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_source ON documents(source_id);
CREATE INDEX idx_documents_domains ON documents USING GIN(domains);
CREATE INDEX idx_documents_epistemic ON documents(epistemic_state);
CREATE INDEX idx_documents_processed ON documents(processing_status);
CREATE INDEX idx_documents_created ON documents(created_at);
CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);
```

**Constraints:**

```sql
ALTER TABLE documents ADD CONSTRAINT documents_content_hash_unique UNIQUE (content_hash);
```

---

### 6. `observations` — Observaciones Extraídas

**Propósito:** Observaciones extraídas de documentos (NER, eventos, entidades)

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `document_id` | UUID | NO | - | Documento origen (references documents) |
| `text` | TEXT | NO | - | Texto de la observación |
| `text_hash` | VARCHAR(64) | NO | - | Hash del texto (único) |
| `start_offset` | INTEGER | SÍ | - | Offset inicial en documento |
| `end_offset` | INTEGER | SÍ | - | Offset final en documento |
| `page_number` | INTEGER | SÍ | - | Número de página (si PDF) |
| `type` | observation_type | NO | - | Tipo (EVENT, STATE, TREND, ANOMALY, etc.) |
| `domains` | analysis_domain[] | SÍ | - | Dominios relacionados |
| `entities` | JSONB | SÍ | - | Entidades extraídas (NER) |
| `keywords` | TEXT[] | SÍ | - | Palabras clave |
| `observed_at` | TIMESTAMPTZ | SÍ | - | Cuándo ocurrió lo observado |
| `extracted_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se extrajo |
| `confidence_score` | DECIMAL(5,4) | SÍ | - | Confianza de extracción (0-1) |
| `extraction_method` | VARCHAR(100) | SÍ | - | Método (AI, regex, manual) |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `created_by` | UUID | SÍ | - | Usuario que extrajo (o null si AI) |

**Índices:**

```sql
CREATE INDEX idx_observations_document ON observations(document_id);
CREATE INDEX idx_observations_type ON observations(type);
CREATE INDEX idx_observations_domains ON observations USING GIN(domains);
CREATE INDEX idx_observations_keywords ON observations USING GIN(keywords);
CREATE INDEX idx_observations_observed_at ON observations(observed_at);
CREATE INDEX idx_observations_text_trgm ON observations USING GIN(text gin_trgm_ops);
```

**Constraints:**

```sql
ALTER TABLE observations ADD CONSTRAINT observations_text_hash_unique UNIQUE (text_hash);
```

---

### 7. `evidences` — Evidencias

**Propósito:** Evidencias con calidad, independencia, corroboración

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `title` | VARCHAR(500) | NO | - | Título (único) |
| `description` | TEXT | SÍ | - | Descripción |
| `type` | evidence_type | NO | - | Tipo (DIRECT_OBSERVATION, DOCUMENTARY, etc.) |
| `observation_ids` | UUID[] | NO | - | Observaciones relacionadas |
| `quality_score` | DECIMAL(5,4) | SÍ | - | Calidad (0-1) |
| `independence_count` | INTEGER | NO | 1 | Fuentes independientes |
| `corroboration_count` | INTEGER | NO | 0 | Corroboraciones |
| `contradiction_count` | INTEGER | NO | 0 | Contradicciones |
| `is_corroborated` | BOOLEAN | NO | false | Si está corroborada |
| `is_contradicted` | BOOLEAN | NO | false | Si está contradicha |
| `domains` | analysis_domain[] | SÍ | - | Dominios relacionados |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `updated_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se actualizó |
| `created_by` | UUID | SÍ | - | Usuario que creó |

**Índices:**

```sql
CREATE INDEX idx_evidences_type ON evidences(type);
CREATE INDEX idx_evidences_domains ON evidences USING GIN(domains);
CREATE INDEX idx_evidences_quality ON evidences(quality_score);
CREATE INDEX idx_evidences_corroborated ON evidences(is_corroborated);
```

**Constraints:**

```sql
ALTER TABLE evidences ADD CONSTRAINT evidences_title_unique UNIQUE (title);
```

---

### 8. `claims` — Afirmaciones

**Propósito:** Afirmaciones con estado epistemológico y evolución temporal

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `text` | TEXT | NO | - | Texto de la afirmación |
| `text_hash` | VARCHAR(64) | NO | - | Hash del texto (único) |
| `title` | VARCHAR(500) | SÍ | - | Título corto |
| `epistemic_state` | epistemic_state | NO | DECLARATION | Estado epistemológico |
| `confidence_score` | DECIMAL(5,4) | SÍ | - | Confianza (0-1) |
| `uncertainty_score` | DECIMAL(5,4) | SÍ | - | Incertidumbre (0-1) |
| `supporting_evidence_ids` | UUID[] | SÍ | - | Evidencias que soportan |
| `contradicting_evidence_ids` | UUID[] | SÍ | - | Evidencias que contradicen |
| `source_ids` | UUID[] | SÍ | - | Fuentes relacionadas |
| `document_ids` | UUID[] | SÍ | - | Documentos relacionados |
| `domains` | analysis_domain[] | SÍ | - | Dominios relacionados |
| `first_seen_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se vio primero |
| `last_updated_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se actualizó |
| `trend` | VARCHAR(20) | SÍ | - | Tendencia (INCREASING, DECREASING, STABLE) |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `created_by` | UUID | SÍ | - | Usuario que creó |

**Índices:**

```sql
CREATE INDEX idx_claims_epistemic ON claims(epistemic_state);
CREATE INDEX idx_claims_domains ON claims USING GIN(domains);
CREATE INDEX idx_claims_confidence ON claims(confidence_score);
CREATE INDEX idx_claims_created ON claims(created_at);
CREATE INDEX idx_claims_text_trgm ON claims USING GIN(text gin_trgm_ops);
```

**Constraints:**

```sql
ALTER TABLE claims ADD CONSTRAINT claims_text_hash_unique UNIQUE (text_hash);
```

---

### 9. `hypotheses` — Hipótesis

**Propósito:** Hipótesis competidoras con evidencias a favor/en contra

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `title` | VARCHAR(500) | NO | - | Título (único) |
| `description` | TEXT | NO | - | Descripción |
| `type` | hypothesis_type | NO | - | Tipo (EXPLANATORY, PREDICTIVE, CAUSAL, etc.) |
| `status` | VARCHAR(50) | NO | PROPOSED | Estado (PROPOSED, EVALUATING, SUPPORTED, REFUTED) |
| `confidence_score` | DECIMAL(5,4) | SÍ | - | Confianza (0-1) |
| `supporting_evidence_ids` | UUID[] | SÍ | - | Evidencias que soportan |
| `contradicting_evidence_ids` | UUID[] | SÍ | - | Evidencias que contradicen |
| `explains_claim_ids` | UUID[] | SÍ | - | Afirmaciones que explica |
| `domains` | analysis_domain[] | SÍ | - | Dominios relacionados |
| `prior_probability` | DECIMAL(5,4) | SÍ | - | Probabilidad a priori |
| `posterior_probability` | DECIMAL(5,4) | SÍ | - | Probabilidad a posteriori (Bayes) |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |
| `updated_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se actualizó |
| `created_by` | UUID | SÍ | - | Usuario que creó |

**Índices:**

```sql
CREATE INDEX idx_hypotheses_type ON hypotheses(type);
CREATE INDEX idx_hypotheses_status ON hypotheses(status);
CREATE INDEX idx_hypotheses_domains ON hypotheses USING GIN(domains);
CREATE INDEX idx_hypotheses_confidence ON hypotheses(confidence_score);
```

**Constraints:**

```sql
ALTER TABLE hypotheses ADD CONSTRAINT hypotheses_title_unique UNIQUE (title);
```

---

### 10. `competing_hypotheses` — Hipótesis Competidoras

**Propósito:** Relacionar hipótesis que compiten (mutuamente exclusivas o alternativas)

**Columnas:**

| Columna | Tipo | Nullable | Default | Descripción |
|---|---|---|---|---|
| `id` | UUID | NO | uuid_generate_v4() | Identificador único |
| `hypothesis_a_id` | UUID | NO | - | Hipótesis A (references hypotheses) |
| `hypothesis_b_id` | UUID | NO | - | Hipótesis B (references hypotheses) |
| `competition_type` | VARCHAR(50) | SÍ | - | Tipo (MUTUALLY_EXCLUSIVE, ALTERNATIVE_EXPLANATIONS) |
| `notes` | TEXT | SÍ | - | Notas explicativas |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Cuándo se creó |

**Constraints:**

```sql
ALTER TABLE competing_hypotheses ADD CONSTRAINT competing_hypotheses_unique UNIQUE (hypothesis_a_id, hypothesis_b_id);
```

---

*(Continuaría con las 14 tablas restantes: signals, anomalies, risk_assessments, risk_convergences, alerts, scenarios, interventions, emotional_sessions, medical_consultations, audit_log, embeddings, rag_queries, system_config, domain_config, entity_relationships)*

---

## 📊 Vistas

### `domain_epistemic_summary`

**Propósito:** Resumen epistemológico por dominio

```sql
CREATE VIEW domain_epistemic_summary AS
SELECT 
    domain,
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE epistemic_state = 'FACT_DOCUMENTED') as facts,
    COUNT(*) FILTER (WHERE epistemic_state = 'DECLARATION') as declarations,
    COUNT(*) FILTER (WHERE epistemic_state = 'EVIDENCE_SUPPORTED') as supported,
    COUNT(*) FILTER (WHERE epistemic_state = 'EVIDENCE_CONTRADICTED') as contradicted,
    COUNT(*) FILTER (WHERE epistemic_state = 'UNCERTAIN') as uncertain,
    AVG(confidence_score) as avg_confidence
FROM documents, UNNEST(domains) as domain
GROUP BY domain;
```

### `active_alerts_summary`

**Propósito:** Alertas activas por nivel

```sql
CREATE VIEW active_alerts_summary AS
SELECT 
    level,
    COUNT(*) as count,
    ARRAY_AGG(title) as titles
FROM alerts
WHERE status = 'ACTIVE'
GROUP BY level
ORDER BY 
    CASE level 
        WHEN 'CRITICAL' THEN 1 
        WHEN 'DANGER' THEN 2 
        WHEN 'WARNING' THEN 3 
        WHEN 'ATTENTION' THEN 4 
        ELSE 5 
    END;
```

### `domain_risk_summary`

**Propósito:** Riesgos por dominio

```sql
CREATE VIEW domain_risk_summary AS
SELECT 
    domain,
    COUNT(*) as total_risks,
    AVG(risk_score) as avg_risk_score,
    MAX(risk_score) as max_risk_score,
    COUNT(*) FILTER (WHERE type = 'EXISTENTIAL') as existential_risks,
    COUNT(*) FILTER (WHERE type = 'CATASTROPHIC') as catastrophic_risks,
    COUNT(*) FILTER (WHERE status = 'ACTIVE') as active_risks
FROM risk_assessments, UNNEST(domains) as domain
GROUP BY domain;
```

---

## 🔁 Triggers

### `update_updated_at_column`

**Propósito:** Actualizar automáticamente `updated_at` en cada UPDATE

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar a todas las tablas con updated_at
CREATE TRIGGER update_sources_updated_at 
    BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ... (restar tablas)
```

---

## 🔗 Relaciones

### Grafo de Conocimiento

**Tabla:** `entity_relationships`

**Propósito:** Relacionar entidades (documento soporta claim, claim explica hypothesis, etc.)

**Ejemplo:**

```sql
INSERT INTO entity_relationships (entity_a_type, entity_a_id, entity_b_type, entity_b_id, relationship_type, strength, confidence)
VALUES 
('DOCUMENT', 'doc-uuid-1', 'OBSERVATION', 'obs-uuid-1', 'CONTAINS', 1.0, 1.0),
('OBSERVATION', 'obs-uuid-1', 'EVIDENCE', 'ev-uuid-1', 'SUPPORTS', 0.9, 0.95),
('EVIDENCE', 'ev-uuid-1', 'CLAIM', 'claim-uuid-1', 'SUPPORTS', 0.85, 0.9),
('CLAIM', 'claim-uuid-1', 'HYPOTHESIS', 'hyp-uuid-1', 'EXPLAINS', 0.8, 0.85);
```

---

## 📈 Índices de Rendimiento

### Índices Críticos

```sql
-- Búsquedas por dominio (GIN para arrays)
CREATE INDEX idx_documents_domains ON documents USING GIN(domains);
CREATE INDEX idx_observations_domains ON observations USING GIN(domains);
CREATE INDEX idx_evidences_domains ON evidences USING GIN(domains);

-- Búsquedas de texto (trigram)
CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);
CREATE INDEX idx_observations_text_trgm ON observations USING GIN(text gin_trgm_ops);
CREATE INDEX idx_claims_text_trgm ON claims USING GIN(text gin_trgm_ops);

-- Búsquedas vectoriales (HNSW para pgvector)
CREATE INDEX idx_embeddings_vector ON embeddings USING HNSW (embedding vector_cosine_ops);

-- Auditoría (búsquedas por fecha, usuario, acción)
CREATE INDEX idx_audit_created ON audit_log(created_at);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
```

---

## 🔐 Seguridad a Nivel de Base de Datos

### Row-Level Security (RLS)

**Ejemplo: Solo Owner puede ver medical_consultations**

```sql
ALTER TABLE medical_consultations ENABLE ROW LEVEL SECURITY;

-- Policy: Solo profesionales médicos pueden ver todas
CREATE POLICY medical_professionals_can_view_all 
ON medical_consultations 
FOR SELECT 
USING (current_setting('app.current_user_role') = 'MEDICAL_PROFESSIONAL');

-- Policy: Usuarios solo ven sus propias consultas
CREATE POLICY users_can_view_own 
ON medical_consultations 
FOR SELECT 
USING (user_id = current_setting('app.current_user_id')::uuid);
```

### Encriptación a Nivel de Columna

```sql
-- Encriptar datos médicos
UPDATE medical_consultations 
SET symptoms_encrypted = pgp_sym_encrypt(symptoms::text, current_setting('app.medical_key'))
WHERE symptoms_encrypted IS NULL;

-- Desencriptar para leer
SELECT pgp_sym_decrypt(symptoms_encrypted, current_setting('app.medical_key')) as symptoms
FROM medical_consultations;
```

---

## 📝 Notas de Implementación

### Migraciones

- Usar migraciones SQL versionadas (`001_initial_schema.sql`, `002_add_indexes.sql`, etc.)
- Incluir `DROP` en comentarios para reversibilidad
- Testear en staging antes de producción

### Seeds

- Seeds iniciales en `database/seeds/001_initial_data.sql`
- Seeds completos en `database/seeds/002_complete_seed.sql`
- No hardcodear IDs en aplicación (usar lookups por nombre)

### Backups

- Backup diario con `pg_dump --format=custom --compress=9`
- Retención: 30 días mínimo
- Testear restore mensualmente

---

## 📚 Relacionados

- [Security Policy](../../SECURITY.md) — Encriptación, auditoría, RLS
- [Epistemology Model](../epistemology/model.md) — Estados epistemológicos, cadena de conocimiento
- [API Documentation](../apis/public.md) — Endpoints que usan estas tablas

---

*Esquema vivo. Actualizar con cada cambio significativo.*

**Última actualización:** Septiembre 2026  
**Versión:** 2.0.0
```

***

✅ Listo. **Copia y pega** en `docs/architecture/database-schema.md`.

***

**¿Continuamos con el siguiente archivo?**

**Próximos:**
1. `docs/epistemology/model.md` — Modelo epistemológico
2. `docs/domains/01-biological-health.md` — Dominio biológico/sanitario
3. `docs/apis/public.md` — API pública

Sources
