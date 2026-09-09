-- ============================================
-- CEUTIA — Database Schema v2.0
-- ============================================
-- Propósito: Salvar a la humanidad mediante comprensión territorial
-- Dominios: 10 (biológico, sanitario, ambiental, violencia, polarización, 
--            desinformación, influencia, fronterizo, territorial, infraestructuras)
-- ============================================

-- ============================================
-- EXTENSIONES
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================
-- ENUMS — Tipos fundamentales
-- ============================================

-- Estado epistemológico
CREATE TYPE epistemic_state AS ENUM (
    'FACT_DOCUMENTED',           -- Hecho documentado
    'DECLARATION',               -- Declaración de fuente
    'EVIDENCE_SUPPORTED',        -- Evidencia que soporta
    'EVIDENCE_CONTRADICTED',     -- Evidencia que contradice
    'INFERENCE',                 -- Inferencia lógica
    'HYPOTHESIS',                -- Hipótesis
    'ALTERNATIVE_HYPOTHESIS',    -- Hipótesis alternativa
    'UNCERTAIN',                 -- Incierto
    'DISPROVEN',                 -- Refutado
    'RETRACTED'                  -- Retirado
);

-- Nivel de alerta
CREATE TYPE alert_level AS ENUM (
    'BASELINE',      -- 🟢 Normal
    'ATTENTION',     -- 🟡 Desviación relevante
    'WARNING',       -- 🟠 Múltiples señales
    'DANGER',        -- 🔴 Convergencia significativa
    'CRITICAL'       -- ⚫ Evento extraordinario
);

-- Dominios de análisis (10 dominios principales)
CREATE TYPE analysis_domain AS ENUM (
    'BIOLOGICAL_HEALTH',         -- 1. Riesgo biológico y sanitario
    'ENVIRONMENTAL_CLIMATE',     -- 2. Riesgo ambiental y climático
    'VIOLENCE_ESCALATION',       -- 3. Violencia y escalada
    'SOCIOLOGICAL_POLARIZATION', -- 4. Polarización sociológica
    'DISINFORMATION',            -- 5. Desinformación
    'INFLUENCE_PROPAGANDA',      -- 6. Influencia y propaganda
    'BORDER_GEOPOLITICAL',       -- 7. Fronterizo y geopolítico
    'TERRITORIAL_INTEGRATED',    -- 8. Territorial integrado
    'INFRASTRUCTURE_SERVICES',   -- 9. Infraestructuras y servicios
    'ECONOMIC_SOCIAL'            -- 10. Económico y social
);

-- Tipo de fuente
CREATE TYPE source_type AS ENUM (
    'GOVERNMENT_OFFICIAL',       -- Gobierno oficial
    'GOVERNMENT_AGENCY',         -- Agencia gubernamental
    'INTERNATIONAL_ORG',         -- Organización internacional
    'ACADEMIC_RESEARCH',         -- Investigación académica
    'NEWS_MEDIA',                -- Medios de comunicación
    'SOCIAL_MEDIA',              -- Redes sociales
    'NGO',                       -- ONG
    'THINK_TANK',                -- Think tank
    'CORPORATE',                 -- Corporativo
    'CITIZEN_REPORT',            -- Reporte ciudadano
    'SENSOR_IOT',                -- Sensor IoT
    'SATELLITE',                 -- Datos satelitales
    'HEALTH_SYSTEM',             -- Sistema sanitario
    'ENVIRONMENTAL_MONITOR',     -- Monitor ambiental
    'SECURITY_FORCE',            -- Fuerzas de seguridad
    'BORDER_CONTROL',            -- Control fronterizo
    'FINANCIAL_DATA',            -- Datos financieros
    'TELECOM_DATA',              -- Datos de telecomunicaciones
    'OTHER'                      -- Otro
);

-- Calidad de fuente
CREATE TYPE source_quality AS ENUM (
    'VERIFIED_HIGH',             -- Verificada, alta calidad
    'VERIFIED_MEDIUM',           -- Verificada, calidad media
    'VERIFIED_LOW',              -- Verificada, baja calidad
    'UNVERIFIED',                -- No verificada
    'DISCREDITED',               -- Desacreditada
    'MALICIOUS'                  -- Maliciosa
);

-- Independencia de fuente
CREATE TYPE source_independence AS ENUM (
    'PRIMARY',                   -- Fuente primaria
    'SECONDARY_INDEPENDENT',     -- Secundaria independiente
    'SECONDARY_DEPENDENT',       -- Secundaria dependiente
    'TERTIARY',                  -- Terciaria
    'UNKNOWN'                    -- Desconocida
);

-- Tipo de documento
CREATE TYPE document_type AS ENUM (
    'OFFICIAL_REPORT',           -- Reporte oficial
    'SCIENTIFIC_PAPER',          -- Paper científico
    'NEWS_ARTICLE',              -- Artículo de noticias
    'SOCIAL_MEDIA_POST',         -- Post en redes sociales
    'GOVERNMENT_DOCUMENT',       -- Documento gubernamental
    'LEGAL_DOCUMENT',            -- Documento legal
    'HEALTH_RECORD',             -- Registro sanitario
    'ENVIRONMENTAL_DATA',        -- Datos ambientales
    'ECONOMIC_DATA',             -- Datos económicos
    'SECURITY_REPORT',           -- Reporte de seguridad
    'BORDER_REPORT',             -- Reporte fronterizo
    'SENSOR_DATA',               -- Datos de sensor
    'SATELLITE_IMAGE',           -- Imagen satelital
    'AUDIO_TRANSCRIPT',          -- Transcripción de audio
    'VIDEO_TRANSCRIPT',          -- Transcripción de video
    'DATABASE_RECORD',           -- Registro de base de datos
    'API_RESPONSE',              -- Respuesta de API
    'OTHER'                      -- Otro
);

-- Tipo de observación
CREATE TYPE observation_type AS ENUM (
    'EVENT',                     -- Evento
    'STATE',                     -- Estado
    'TREND',                     -- Tendencia
    'ANOMALY',                   -- Anomalía
    'CORRELATION',               -- Correlación
    'CAUSATION',                 -- Causación
    'PREDICTION',                -- Predicción
    'RETRODICTION'               -- Retrodicción
);

-- Tipo de evidencia
CREATE TYPE evidence_type AS ENUM (
    'DIRECT_OBSERVATION',        -- Observación directa
    'DOCUMENTARY',               -- Documental
    'STATISTICAL',               -- Estadística
    'EXPERT_TESTIMONY',          -- Testimonio de experto
    'PHYSICAL',                  -- Física
    'DIGITAL',                   -- Digital
    'CIRCUMSTANTIAL',            -- Circunstancial
    'ANALOGICAL'                 -- Analógica
);

-- Tipo de hipótesis
CREATE TYPE hypothesis_type AS ENUM (
    'EXPLANATORY',               -- Explicativa
    'PREDICTIVE',                -- Predictiva
    'CAUSAL',                    -- Causal
    'CORRELATIONAL',             -- Correlacional
    'MECHANISTIC',               -- Mecanicista
    'STATISTICAL'                -- Estadística
);

-- Tipo de riesgo
CREATE TYPE risk_type AS ENUM (
    'EXISTENTIAL',               -- Existencial
    'CATASTROPHIC',              -- Catastrófico
    'SEVERE',                    -- Severo
    'MODERATE',                  -- Moderado
    'MINOR'                      -- Menor
);

-- Tipo de intervención
CREATE TYPE intervention_type AS ENUM (
    'INFORMATION_PUBLIC',        -- Información pública (A)
    'EDUCATION',                 -- Educación (B)
    'COMMUNITY_BUILDING',        -- Construcción comunitaria (C)
    'INSTITUTIONAL',             -- Institucional (D)
    'POLICY',                    -- Política (E)
    'TECHNICAL',                 -- Técnica (F)
    'EMERGENCY',                 -- Emergencia (G)
    'PREVENTIVE'                 -- Preventiva
);

-- Tipo de sesión emocional
CREATE TYPE session_type AS ENUM (
    'VOLUNTARY_REFLECTION',      -- Reflexión voluntaria
    'EMOTIONAL_CHECK',           -- Check emocional
    'STRESS_ASSESSMENT',         -- Evaluación de estrés
    'WELLBEING_TRACKING'         -- Seguimiento de bienestar
);

-- Tipo de consulta médica
CREATE TYPE medical_consultation_type AS ENUM (
    'GENERAL_INQUIRY',           -- Consulta general
    'SYMPTOM_CHECK',             -- Check de síntomas
    'PROFESSIONAL_CONSULTATION', -- Consulta profesional
    'FOLLOW_UP'                  -- Seguimiento
);

-- Estado de auditoría
CREATE TYPE audit_action AS ENUM (
    'CREATE',
    'READ',
    'UPDATE',
    'DELETE',
    'EXPORT',
    'IMPORT',
    'LOGIN',
    'LOGOUT',
    'PERMISSION_CHANGE',
    'SECURITY_EVENT',
    'SYSTEM_EVENT',
    'DATA_ACCESS',
    'ALERT_TRIGGERED',
    'MODEL_INFERENCE',
    'RAG_QUERY',
    'EXTERNAL_API_CALL'
);

-- ============================================
-- CORE — Tablas fundamentales
-- ============================================

-- 1. Fuentes autorizadas
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    type source_type NOT NULL,
    quality source_quality NOT NULL DEFAULT 'UNVERIFIED',
    independence source_independence NOT NULL DEFAULT 'UNKNOWN',
    
    -- Metadatos de fuente
    url VARCHAR(2048),
    official_name VARCHAR(500),
    country VARCHAR(100),
    region VARCHAR(100),
    language VARCHAR(10),
    
    -- Trazabilidad
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    
    -- Clasificación
    domains analysis_domain[],
    tags TEXT[],
    
    -- Estado
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_blocked BOOLEAN NOT NULL DEFAULT false,
    blocked_reason TEXT,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT sources_name_unique UNIQUE (name),
    CONSTRAINT sources_url_unique UNIQUE (url)
);

-- Índices para fuentes
CREATE INDEX idx_sources_type ON sources(type);
CREATE INDEX idx_sources_quality ON sources(quality);
CREATE INDEX idx_sources_domains ON sources USING GIN(domains);
CREATE INDEX idx_sources_tags ON sources USING GIN(tags);
CREATE INDEX idx_sources_active ON sources(is_active);
CREATE INDEX idx_sources_name_trgm ON sources USING GIN(name gin_trgm_ops);

-- 2. Usuarios (sistema de autenticación)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    
    -- Autenticación
    password_hash VARCHAR(255) NOT NULL,
    mfa_enabled BOOLEAN NOT NULL DEFAULT false,
    mfa_secret VARCHAR(255),
    
    -- Perfil
    full_name VARCHAR(255),
    role VARCHAR(100) NOT NULL DEFAULT 'CITIZEN',
    organization VARCHAR(255),
    
    -- Estado
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    last_login_at TIMESTAMPTZ,
    
    -- Seguridad
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT users_email_unique UNIQUE (email),
    CONSTRAINT users_username_unique UNIQUE (username)
);

-- Índices para usuarios
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- 3. Roles y permisos
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, role_id)
);

-- 4. Documentos
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type document_type NOT NULL,
    
    -- Contenido
    content_hash VARCHAR(64) NOT NULL, -- SHA-256
    content_type VARCHAR(100),
    content_size_bytes BIGINT,
    language VARCHAR(10),
    
    -- Procedencia
    source_id UUID NOT NULL REFERENCES sources(id),
    original_url VARCHAR(2048),
    published_at TIMESTAMPTZ,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Dominios
    domains analysis_domain[],
    
    -- Estado epistemológico
    epistemic_state epistemic_state NOT NULL DEFAULT 'DECLARATION',
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Storage
    storage_provider VARCHAR(50),
    storage_bucket VARCHAR(255),
    storage_key VARCHAR(500),
    storage_url VARCHAR(2048),
    
    -- Procesamiento
    processing_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    processed_at TIMESTAMPTZ,
    processing_error TEXT,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT documents_content_hash_unique UNIQUE (content_hash)
);

-- Índices para documentos
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_source ON documents(source_id);
CREATE INDEX idx_documents_domains ON documents USING GIN(domains);
CREATE INDEX idx_documents_epistemic ON documents(epistemic_state);
CREATE INDEX idx_documents_processed ON documents(processing_status);
CREATE INDEX idx_documents_created ON documents(created_at);
CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);

-- 5. Observaciones (extracciones de documentos)
CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Contenido
    text TEXT NOT NULL,
    text_hash VARCHAR(64) NOT NULL,
    start_offset INTEGER,
    end_offset INTEGER,
    page_number INTEGER,
    
    -- Clasificación
    type observation_type NOT NULL,
    domains analysis_domain[],
    entities JSONB, -- Entidades extraídas (NER)
    keywords TEXT[],
    
    -- Metadatos temporales
    observed_at TIMESTAMPTZ, -- Cuándo ocurrió lo observado
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Calidad
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    extraction_method VARCHAR(100), -- Manual, AI, regex, etc.
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT observations_text_hash_unique UNIQUE (text_hash)
);

-- Índices para observaciones
CREATE INDEX idx_observations_document ON observations(document_id);
CREATE INDEX idx_observations_type ON observations(type);
CREATE INDEX idx_observations_domains ON observations USING GIN(domains);
CREATE INDEX idx_observations_keywords ON observations USING GIN(keywords);
CREATE INDEX idx_observations_observed_at ON observations(observed_at);
CREATE INDEX idx_observations_text_trgm ON observations USING GIN(text gin_trgm_ops);

-- ============================================
-- EPISTEMIC CORE — Núcleo epistemológico
-- ============================================

-- 6. Evidencias
CREATE TABLE evidences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Contenido
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type evidence_type NOT NULL,
    
    -- Relación con observaciones
    observation_ids UUID[] NOT NULL REFERENCES observations(id),
    
    -- Calidad
    quality_score DECIMAL(5,4) CHECK (quality_score >= 0 AND quality_score <= 1),
    independence_count INTEGER NOT NULL DEFAULT 1, -- Cuántas fuentes independientes
    corroboration_count INTEGER NOT NULL DEFAULT 0, -- Cuántas corroboraciones
    contradiction_count INTEGER NOT NULL DEFAULT 0, -- Cuántas contradicciones
    
    -- Estado
    is_corroborated BOOLEAN NOT NULL DEFAULT false,
    is_contradicted BOOLEAN NOT NULL DEFAULT false,
    
    -- Dominios
    domains analysis_domain[],
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT evidences_title_unique UNIQUE (title)
);

-- Índices para evidencias
CREATE INDEX idx_evidences_type ON evidences(type);
CREATE INDEX idx_evidences_domains ON evidences USING GIN(domains);
CREATE INDEX idx_evidences_quality ON evidences(quality_score);
CREATE INDEX idx_evidences_corroborated ON evidences(is_corroborated);

-- 7. Afirmaciones (claims)
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Contenido
    text TEXT NOT NULL,
    text_hash VARCHAR(64) NOT NULL,
    title VARCHAR(500),
    
    -- Estado epistemológico
    epistemic_state epistemic_state NOT NULL DEFAULT 'DECLARATION',
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    uncertainty_score DECIMAL(5,4) CHECK (uncertainty_score >= 0 AND uncertainty_score <= 1),
    
    -- Evidencias
    supporting_evidence_ids UUID[] REFERENCES evidences(id),
    contradicting_evidence_ids UUID[] REFERENCES evidences(id),
    
    -- Fuentes
    source_ids UUID[] REFERENCES sources(id),
    document_ids UUID[] REFERENCES documents(id),
    
    -- Dominios
    domains analysis_domain[],
    
    -- Evolución temporal
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trend VARCHAR(20), -- 'INCREASING', 'DECREASING', 'STABLE'
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT claims_text_hash_unique UNIQUE (text_hash)
);

-- Índices para afirmaciones
CREATE INDEX idx_claims_epistemic ON claims(epistemic_state);
CREATE INDEX idx_claims_domains ON claims USING GIN(domains);
CREATE INDEX idx_claims_confidence ON claims(confidence_score);
CREATE INDEX idx_claims_created ON claims(created_at);
CREATE INDEX idx_claims_text_trgm ON claims USING GIN(text gin_trgm_ops);

-- 8. Hipótesis
CREATE TABLE hypotheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Contenido
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    type hypothesis_type NOT NULL,
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'PROPOSED', -- PROPOSED, EVALUATING, SUPPORTED, REFUTED
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Evidencias
    supporting_evidence_ids UUID[] REFERENCES evidences(id),
    contradicting_evidence_ids UUID[] REFERENCES evidences(id),
    
    -- Relación con afirmaciones
    explains_claim_ids UUID[] REFERENCES claims(id),
    
    -- Dominios
    domains analysis_domain[],
    
    -- Probabilidad
    prior_probability DECIMAL(5,4),
    posterior_probability DECIMAL(5,4),
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT hypotheses_title_unique UNIQUE (title)
);

-- Índices para hipótesis
CREATE INDEX idx_hypotheses_type ON hypotheses(type);
CREATE INDEX idx_hypotheses_status ON hypotheses(status);
CREATE INDEX idx_hypotheses_domains ON hypotheses USING GIN(domains);
CREATE INDEX idx_hypotheses_confidence ON hypotheses(confidence_score);

-- 9. Hipótesis competidoras (relaciones)
CREATE TABLE competing_hypotheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hypothesis_a_id UUID NOT NULL REFERENCES hypotheses(id) ON DELETE CASCADE,
    hypothesis_b_id UUID NOT NULL REFERENCES hypotheses(id) ON DELETE CASCADE,
    competition_type VARCHAR(50), -- 'MUTUALLY_EXCLUSIVE', 'ALTERNATIVE_EXPLANATIONS', etc.
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT competing_hypotheses_unique UNIQUE (hypothesis_a_id, hypothesis_b_id)
);

-- ============================================
-- SIGNALS & ANOMALIES — Señales y anomalías
-- ============================================

-- 10. Señales (signals)
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Contenido
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Clasificación
    type VARCHAR(100) NOT NULL,
    domains analysis_domain[],
    
    -- Métricas cuantitativas
    magnitude DECIMAL(10,4), -- Magnitud de la señal
    velocity DECIMAL(10,4), -- Velocidad de cambio
    acceleration DECIMAL(10,4), -- Aceleración del cambio
    
    -- Estado
    is_anomalous BOOLEAN NOT NULL DEFAULT false,
    anomaly_score DECIMAL(5,4), -- Qué tan anómala es
    baseline_value DECIMAL(10,4), -- Valor baseline histórico
    
    -- Temporal
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    
    -- Fuentes
    observation_ids UUID[] REFERENCES observations(id),
    evidence_ids UUID[] REFERENCES evidences(id),
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT signals_title_unique UNIQUE (title)
);

-- Índices para señales
CREATE INDEX idx_signals_type ON signals(type);
CREATE INDEX idx_signals_domains ON signals USING GIN(domains);
CREATE INDEX idx_signals_anomalous ON signals(is_anomalous);
CREATE INDEX idx_signals_detected ON signals(detected_at);
CREATE INDEX idx_signals_magnitude ON signals(magnitude);

-- 11. Anomalías detectadas
CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relación con señales
    signal_id UUID NOT NULL REFERENCES signals(id),
    
    -- Tipo de anomalía
    anomaly_type VARCHAR(100) NOT NULL, -- STATISTICAL, CONTEXTUAL, COLLECTIVE, etc.
    
    -- Detección
    detection_method VARCHAR(100) NOT NULL, -- ZSCORE, ISOLATION_FOREST, etc.
    detection_score DECIMAL(5,4) NOT NULL, -- Score de detección
    threshold DECIMAL(5,4), -- Umbral usado
    
    -- Descripción
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    
    -- Impacto potencial
    potential_impact TEXT,
    affected_domains analysis_domain[],
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'DETECTED', -- DETECTED, INVESTIGATING, CONFIRMED, FALSE_POSITIVE, RESOLVED
    confirmed_at TIMESTAMPTZ,
    confirmed_by UUID REFERENCES users(id),
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT anomalies_signal_unique UNIQUE (signal_id)
);

-- Índices para anomalías
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX idx_anomalies_severity ON anomalies(severity);
CREATE INDEX idx_anomalies_status ON anomalies(status);
CREATE INDEX idx_anomalies_domains ON anomalies USING GIN(affected_domains);

-- ============================================
-- RISK ASSESSMENT — Evaluación de riesgos
-- ============================================

-- 12. Evaluaciones de riesgo
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Clasificación
    type risk_type NOT NULL,
    domains analysis_domain[],
    
    -- Componentes de riesgo
    probability DECIMAL(5,4) NOT NULL CHECK (probability >= 0 AND probability <= 1),
    impact DECIMAL(5,4) NOT NULL CHECK (impact >= 0 AND impact <= 5),
    vulnerability DECIMAL(5,4) CHECK (vulnerability >= 0 AND vulnerability <= 1),
    risk_score DECIMAL(5,4) NOT NULL, -- probability * impact * vulnerability
    
    -- Condiciones
    conditions JSONB, -- Condiciones que activan/modulan el riesgo
    triggers TEXT[], -- Triggers que activan el riesgo
    
    -- Evidencias
    evidence_ids UUID[] REFERENCES evidences(id),
    signal_ids UUID[] REFERENCES signals(id),
    anomaly_ids UUID[] REFERENCES anomalies(id),
    
    -- Hipótesis relacionadas
    hypothesis_ids UUID[] REFERENCES hypotheses(id),
    
    -- Temporal
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    review_at TIMESTAMPTZ, -- Cuándo revisar
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, MONITORING, MITIGATED, CLOSED
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT risk_assessments_title_unique UNIQUE (title)
);

-- Índices para evaluaciones de riesgo
CREATE INDEX idx_risk_type ON risk_assessments(type);
CREATE INDEX idx_risk_domains ON risk_assessments USING GIN(domains);
CREATE INDEX idx_risk_score ON risk_assessments(risk_score);
CREATE INDEX idx_risk_status ON risk_assessments(status);

-- 13. Convergencias de riesgo (múltiples dominios)
CREATE TABLE risk_convergences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Riesgos convergentes
    risk_assessment_ids UUID[] NOT NULL REFERENCES risk_assessments(id),
    
    -- Dominios involucrados
    domains analysis_domain[] NOT NULL,
    
    -- Tipo de convergencia
    convergence_type VARCHAR(100), -- CASCADING, COMPOUND, SYNERGISTIC, etc.
    
    -- Impacto combinado
    combined_risk_score DECIMAL(5,4) NOT NULL,
    amplification_factor DECIMAL(5,4), -- Cuánto se amplifica el riesgo
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'DETECTED',
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT risk_convergences_title_unique UNIQUE (title)
);

-- Índices para convergencias
CREATE INDEX idx_convergences_domains ON risk_convergences USING GIN(domains);
CREATE INDEX idx_convergences_score ON risk_convergences(combined_risk_score);

-- ============================================
-- ALERTS — Sistema de alertas
-- ============================================

-- 14. Alertas
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Nivel
    level alert_level NOT NULL,
    
    -- Dominios afectados
    domains analysis_domain[] NOT NULL,
    
    -- Causas
    risk_assessment_ids UUID[] REFERENCES risk_assessments(id),
    convergence_ids UUID[] REFERENCES risk_convergences(id),
    anomaly_ids UUID[] REFERENCES anomalies(id),
    signal_ids UUID[] REFERENCES signals(id),
    
    -- Explicación (para transparencia)
    explanation TEXT, -- Por qué se activó esta alerta
    evidence_summary TEXT, -- Resumen de evidencias
    
    -- Acciones recomendadas
    recommended_actions TEXT[],
    intervention_types intervention_type[],
    
    -- Temporal
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, ACKNOWLEDGED, RESOLVED, FALSE_ALARM
    
    -- Notificaciones
    notifications_sent BOOLEAN NOT NULL DEFAULT false,
    notification_channels TEXT[], -- EMAIL, TELEGRAM, SMS, etc.
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT alerts_title_unique UNIQUE (title)
);

-- Índices para alertas
CREATE INDEX idx_alerts_level ON alerts(level);
CREATE INDEX idx_alerts_domains ON alerts USING GIN(domains);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_triggered ON alerts(triggered_at);

-- ============================================
-- SCENARIOS — Escenarios futuros
-- ============================================

-- 15. Escenarios
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Tipo
    scenario_type VARCHAR(100), -- BASELINE, OPTIMISTIC, PESSIMISTIC, WORST_CASE, etc.
    domains analysis_domain[],
    
    -- Supuestos
    assumptions TEXT[] NOT NULL, -- Supuestos del escenario
    
    -- Probabilidad
    probability DECIMAL(5,4) CHECK (probability >= 0 AND probability <= 1),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Temporal
    time_horizon VARCHAR(50), -- SHORT_TERM, MEDIUM_TERM, LONG_TERM
    horizon_months INTEGER,
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    
    -- Elementos del escenario
    risk_assessment_ids UUID[] REFERENCES risk_assessments(id),
    hypothesis_ids UUID[] REFERENCES hypotheses(id),
    signal_ids UUID[] REFERENCES signals(id),
    
    -- Impacto esperado
    expected_impact TEXT,
    impact_severity risk_type,
    
    -- Indicadores de seguimiento
    tracking_indicators TEXT[],
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT scenarios_title_unique UNIQUE (title)
);

-- Índices para escenarios
CREATE INDEX idx_scenarios_type ON scenarios(scenario_type);
CREATE INDEX idx_scenarios_domains ON scenarios USING GIN(domains);
CREATE INDEX idx_scenarios_probability ON scenarios(probability);

-- ============================================
-- INTERVENTIONS — Intervenciones
-- ============================================

-- 16. Intervenciones (acciones para mitigar riesgos)
CREATE TABLE interventions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Tipo
    type intervention_type NOT NULL,
    domains analysis_domain[],
    
    -- Relación con alertas/riesgos
    alert_ids UUID[] REFERENCES alerts(id),
    risk_assessment_ids UUID[] REFERENCES risk_assessments(id),
    
    -- Detalles
    actions TEXT[] NOT NULL, -- Acciones concretas
    expected_outcome TEXT,
    success_metrics TEXT[],
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'PROPOSED', -- PROPOSED, APPROVED, IN_PROGRESS, COMPLETED, CANCELLED
    
    -- Temporal
    proposed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Responsable
    assigned_to UUID REFERENCES users(id),
    
    -- Resultados
    actual_outcome TEXT,
    effectiveness_score DECIMAL(5,4),
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT interventions_title_unique UNIQUE (title)
);

-- Índices para intervenciones
CREATE INDEX idx_interventions_type ON interventions(type);
CREATE INDEX idx_interventions_status ON interventions(status);
CREATE INDEX idx_interventions_domains ON interventions USING GIN(domains);

-- ============================================
-- MEDICAL MODULE — Módulo médico (perímetro independiente)
-- ============================================

-- 17. Sesiones emocionales (voluntarias)
CREATE TABLE emotional_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Tipo
    type session_type NOT NULL,
    
    -- Contenido (encriptado)
    content_hash VARCHAR(64),
    -- El contenido real va en storage encriptado, no en DB
    
    -- Estado emocional (auto-reportado)
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10),
    
    -- Metadatos
    duration_minutes INTEGER,
    notes TEXT,
    
    -- Estado
    is_completed BOOLEAN NOT NULL DEFAULT false,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Constraints
    -- No hay constraints únicos porque un usuario puede tener múltiples sesiones
    CONSTRAINT emotional_sessions_user_check CHECK (user_id IS NOT NULL)
);

-- Índices para sesiones emocionales
CREATE INDEX idx_emotional_sessions_user ON emotional_sessions(user_id);
CREATE INDEX idx_emotional_sessions_type ON emotional_sessions(type);
CREATE INDEX idx_emotional_sessions_created ON emotional_sessions(created_at);

-- 18. Consultas médicas
CREATE TABLE medical_consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    professional_id UUID REFERENCES users(id), -- El profesional (Dr. Román)
    
    -- Tipo
    type medical_consultation_type NOT NULL,
    
    -- Contenido (encriptado, en storage)
    content_hash VARCHAR(64),
    
    -- Síntomas (estructurado)
    symptoms JSONB, -- {symptom: severity, ...}
    
    -- Diagnóstico (solo profesional)
    diagnosis TEXT,
    diagnosis_code VARCHAR(50), -- ICD-10
    
    -- Recomendaciones
    recommendations TEXT[],
    prescriptions TEXT[],
    referrals TEXT[],
    
    -- Estado
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN', -- OPEN, IN_PROGRESS, CLOSED, REFERRED
    
    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    
    -- Auditoría
    created_by UUID REFERENCES users(id),
    
    -- HIPAA/GDPR compliance flags
    is_encrypted BOOLEAN NOT NULL DEFAULT true,
    is_hipaa_compliant BOOLEAN NOT NULL DEFAULT true,
    
    -- Constraints
    CONSTRAINT medical_consultations_user_check CHECK (user_id IS NOT NULL)
);

-- Índices para consultas médicas
CREATE INDEX idx_medical_consultations_user ON medical_consultations(user_id);
CREATE INDEX idx_medical_consultations_professional ON medical_consultations(professional_id);
CREATE INDEX idx_medical_consultations_status ON medical_consultations(status);
CREATE INDEX idx_medical_consultations_created ON medical_consultations(created_at);

-- ============================================
-- AUDIT — Auditoría completa
-- ============================================

-- 19. Auditoría (inmutable)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Acción
    action audit_action NOT NULL,
    
    -- Entidad afectada
    entity_type VARCHAR(100), -- 'USER', 'DOCUMENT', 'CLAIM', etc.
    entity_id UUID,
    
    -- Usuario
    user_id UUID REFERENCES users(id),
    
    -- Detalles
    description TEXT,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    
    -- Resultado
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    
    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para auditoría
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);
CREATE INDEX idx_audit_success ON audit_log(success);

-- ============================================
-- AI/RAG — Capa de IA y RAG
-- ============================================

-- 20. Embeddings (para RAG)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relación con documento/observación
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    observation_id UUID REFERENCES observations(id) ON DELETE CASCADE,
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    
    -- Vector (usando pgvector)
    embedding vector(1536), -- OpenAI ada-002, cambiar según modelo
    
    -- Metadatos
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    dimensions INTEGER NOT NULL,
    
    -- Chunk info
    chunk_index INTEGER,
    chunk_start INTEGER,
    chunk_end INTEGER,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT embeddings_entity_check CHECK (
        (document_id IS NOT NULL AND observation_id IS NULL AND claim_id IS NULL) OR
        (document_id IS NULL AND observation_id IS NOT NULL AND claim_id IS NULL) OR
        (document_id IS NULL AND observation_id IS NULL AND claim_id IS NOT NULL)
    )
);

-- Índices para embeddings (búsqueda vectorial)
CREATE INDEX idx_embeddings_document ON embeddings(document_id);
CREATE INDEX idx_embeddings_observation ON embeddings(observation_id);
CREATE INDEX idx_embeddings_claim ON embeddings(claim_id);
CREATE INDEX idx_embeddings_vector ON embeddings USING HNSW (embedding vector_cosine_ops);

-- 21. Consultas RAG
CREATE TABLE rag_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Consulta
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64),
    
    -- Resultados
    result_document_ids UUID[],
    result_observation_ids UUID[],
    result_claim_ids UUID[],
    result_count INTEGER,
    
    -- Parámetros
    top_k INTEGER,
    similarity_threshold DECIMAL(5,4),
    
    -- Contexto
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100),
    
    -- Respuesta
    response_text TEXT,
    response_model VARCHAR(100),
    
    -- Temporal
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Auditoría
    created_by UUID REFERENCES users(id)
);

-- Índices para queries RAG
CREATE INDEX idx_rag_queries_user ON rag_queries(user_id);
CREATE INDEX idx_rag_queries_created ON rag_queries(created_at);

-- ============================================
-- CONFIGURATION — Configuración del sistema
-- ============================================

-- 22. Configuración del sistema
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Clave única
    key VARCHAR(255) NOT NULL UNIQUE,
    
    -- Valor (JSON para flexibilidad)
    value JSONB NOT NULL,
    
    -- Descripción
    description TEXT,
    
    -- Tipo
    config_type VARCHAR(50), -- STRING, NUMBER, BOOLEAN, JSON, etc.
    
    -- Ámbito
    scope VARCHAR(50), -- GLOBAL, DOMAIN, USER, etc.
    domain analysis_domain,
    
    -- Estado
    is_active BOOLEAN NOT NULL DEFAULT true,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT system_config_key_unique UNIQUE (key)
);

-- Índices para configuración
CREATE INDEX idx_system_config_key ON system_config(key);
CREATE INDEX idx_system_config_type ON system_config(config_type);
CREATE INDEX idx_system_config_domain ON system_config(domain);

-- 23. Configuración de dominios
CREATE TABLE domain_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain analysis_domain NOT NULL UNIQUE,
    
    -- Configuración específica del dominio
    config JSONB NOT NULL,
    
    -- Estado
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    is_public BOOLEAN NOT NULL DEFAULT false, -- Visible al público o solo Owner
    
    -- Umbrales de alerta
    alert_thresholds JSONB,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Índices para configuración de dominios
CREATE INDEX idx_domain_config_domain ON domain_config(domain);
CREATE INDEX idx_domain_config_enabled ON domain_config(is_enabled);

-- ============================================
-- RELATIONSHIPS — Relaciones y grafos
-- ============================================

-- 24. Relaciones entre entidades (grafo de conocimiento)
CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Entidades relacionadas
    entity_a_type VARCHAR(100) NOT NULL, -- 'DOCUMENT', 'CLAIM', 'EVIDENCE', etc.
    entity_a_id UUID NOT NULL,
    entity_b_type VARCHAR(100) NOT NULL,
    entity_b_id UUID NOT NULL,
    
    -- Tipo de relación
    relationship_type VARCHAR(100) NOT NULL, -- SUPPORTS, CONTRADICTS, EXPLAINS, CAUSES, CORRELATES, etc.
    
    -- Fuerza de relación
    strength DECIMAL(5,4) CHECK (strength >= 0 AND strength <= 1),
    confidence DECIMAL(5,4) CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Descripción
    description TEXT,
    
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT entity_relationships_unique UNIQUE (entity_a_type, entity_a_id, entity_b_type, entity_b_id, relationship_type)
);

-- Índices para relaciones
CREATE INDEX idx_entity_relationships_a ON entity_relationships(entity_a_type, entity_a_id);
CREATE INDEX idx_entity_relationships_b ON entity_relationships(entity_b_type, entity_b_id);
CREATE INDEX idx_entity_relationships_type ON entity_relationships(relationship_type);

-- ============================================
-- VIEWS — Vistas útiles
-- ============================================

-- Vista: Resumen de estado epistemológico por dominio
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

-- Vista: Alertas activas por nivel
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

-- Vista: Riesgos por dominio
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

-- ============================================
-- TRIGGERS — Triggers automáticos
-- ============================================

-- Trigger: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a tablas con updated_at
CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_evidences_updated_at BEFORE UPDATE ON evidences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_claims_updated_at BEFORE UPDATE ON claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hypotheses_updated_at BEFORE UPDATE ON hypotheses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_assessments_updated_at BEFORE UPDATE ON risk_assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON scenarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON interventions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_domain_config_updated_at BEFORE UPDATE ON domain_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SEED DATA — Datos iniciales críticos
-- ============================================

-- Insertar configuración de los 10 dominios
INSERT INTO domain_config (domain, config, is_enabled, is_public, alert_thresholds) VALUES
('BIOLOGICAL_HEALTH', 
 '{"monitoring_enabled": true, "data_sources": ["health_systems", "environmental_monitors"], "update_frequency": "daily"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),

('ENVIRONMENTAL_CLIMATE', 
 '{"monitoring_enabled": true, "data_sources": ["satellites", "sensors", "government_reports"], "update_frequency": "hourly"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),

('VIOLENCE_ESCALATION', 
 '{"monitoring_enabled": true, "data_sources": ["security_forces", "news_media", "social_media"], "update_frequency": "realtime"}'::jsonb,
 true, false,
 '{"attention": 0.2, "warning": 0.4, "danger": 0.6, "critical": 0.8}'::jsonb),

('SOCIOLOGICAL_POLARIZATION', 
 '{"monitoring_enabled": true, "data_sources": ["social_media", "surveys", "academic_research"], "update_frequency": "daily"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.85}'::jsonb),

('DISINFORMATION', 
 '{"monitoring_enabled": true, "data_sources": ["fact_checkers", "social_media", "news_media"], "update_frequency": "realtime"}'::jsonb,
 true, false,
 '{"attention": 0.25, "warning": 0.45, "danger": 0.65, "critical": 0.85}'::jsonb),

('INFLUENCE_PROPAGANDA', 
 '{"monitoring_enabled": true, "data_sources": ["social_media", "think_tanks", "government_documents"], "update_frequency": "daily"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),

('BORDER_GEOPOLITICAL', 
 '{"monitoring_enabled": true, "data_sources": ["border_control", "government_documents", "international_orgs"], "update_frequency": "daily"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),

('TERRITORIAL_INTEGRATED', 
 '{"monitoring_enabled": true, "data_sources": ["all_domains"], "update_frequency": "hourly"}'::jsonb,
 true, false,
 '{"attention": 0.35, "warning": 0.55, "danger": 0.75, "critical": 0.9}'::jsonb),

('INFRASTRUCTURE_SERVICES', 
 '{"monitoring_enabled": true, "data_sources": ["government_agencies", "sensors", "citizen_reports"], "update_frequency": "hourly"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),

('ECONOMIC_SOCIAL', 
 '{"monitoring_enabled": true, "data_sources": ["financial_data", "government_reports", "academic_research"], "update_frequency": "daily"}'::jsonb,
 true, false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb);

-- Insertar configuración del sistema
INSERT INTO system_config (key, value, description, config_type, scope) VALUES
('system.name', '"CEUTIA"', 'Nombre del sistema', 'STRING', 'GLOBAL'),
('system.version', '"2.0.0"', 'Versión del sistema', 'STRING', 'GLOBAL'),
('system.environment', '"development"', 'Entorno (development, staging, production)', 'STRING', 'GLOBAL'),
('ai.provider', '"openai"', 'Proveedor de IA', 'STRING', 'GLOBAL'),
('ai.model', '"gpt-4"', 'Modelo de IA por defecto', 'STRING', 'GLOBAL'),
('ai.temperature', '0.7', 'Temperatura por defecto', 'NUMBER', 'GLOBAL'),
('rag.top_k', '10', 'Número de resultados RAG', 'NUMBER', 'GLOBAL'),
('rag.similarity_threshold', '0.7', 'Umbral de similitud RAG', 'NUMBER', 'GLOBAL'),
('security.rate_limit', '100', 'Rate limit por minuto', 'NUMBER', 'GLOBAL'),
('security.max_login_attempts', '5', 'Máximos intentos de login', 'NUMBER', 'GLOBAL'),
('audit.enabled', 'true', 'Auditoría habilitada', 'BOOLEAN', 'GLOBAL'),
('medical_module.enabled', 'false', 'Módulo médico habilitado', 'BOOLEAN', 'GLOBAL');

-- ============================================
-- COMENTARIOS — Documentación en DB
-- ============================================

COMMENT ON DATABASE ceutia IS 'CEUTIA — Sistema de Inteligencia Territorial para Salvar a la Humanidad';

COMMENT ON TYPE epistemic_state IS 'Estado epistemológico: desde hecho documentado hasta refutado';
COMMENT ON TYPE alert_level IS 'Niveles de alerta: baseline, attention, warning, danger, critical';
COMMENT ON TYPE analysis_domain IS '10 dominios de análisis para monitorización territorial integral';

COMMENT ON TABLE sources IS 'Fuentes autorizadas con trazabilidad completa';
COMMENT ON TABLE documents IS 'Documentos con procedencia, versionado y estado epistemológico';
COMMENT ON TABLE observations IS 'Observaciones extraídas de documentos';
COMMENT ON TABLE evidences IS 'Evidencias con calidad, independencia y corroboración';
COMMENT ON TABLE claims IS 'Afirmaciones con estado epistemológico y evolución temporal';
COMMENT ON TABLE hypotheses IS 'Hipótesis competidoras con evidencias a favor/en contra';
COMMENT ON TABLE signals IS 'Señales con magnitud, velocidad, aceleración';
COMMENT ON TABLE anomalies IS 'Anomalías detectadas estadísticamente';
COMMENT ON TABLE risk_assessments IS 'Evaluaciones de riesgo con probabilidad, impacto, vulnerabilidad';
COMMENT ON TABLE risk_convergences IS 'Convergencias de riesgo entre múltiples dominios';
COMMENT ON TABLE alerts IS 'Alertas explicables y auditables';
COMMENT ON TABLE scenarios IS 'Escenarios futuros con probabilidades y supuestos';
COMMENT ON TABLE interventions IS 'Intervenciones públicas tipo A-G';
COMMENT ON TABLE emotional_sessions IS 'Sesiones emocionales voluntarias (módulo médico)';
COMMENT ON TABLE medical_consultations IS 'Consultas médicas profesionales (módulo médico)';
COMMENT ON TABLE audit_log IS 'Auditoría completa e inmutable de todas las acciones';
COMMENT ON TABLE embeddings IS 'Embeddings vectoriales para RAG';
COMMENT ON TABLE rag_queries IS 'Consultas RAG con trazabilidad';
COMMENT ON TABLE entity_relationships IS 'Grafo de conocimiento: relaciones entre entidades';

-- ============================================
-- FIN DEL ESQUEMA
-- ============================================
```

***
