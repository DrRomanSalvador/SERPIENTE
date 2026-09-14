-- ============================================
-- CEUTIA — Database Schema v2.0
-- ============================================
-- Propósito: Salvar a la humanidad mediante comprensión territorial
-- Dominios: 10 (biológico, sanitario, ambiental, violencia, polarización,
--            desinformación, influencia, fronterizo, territorial, infraestructuras)
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TYPE epistemic_state AS ENUM ('FACT_DOCUMENTED', 'DECLARATION', 'EVIDENCE_SUPPORTED', 'EVIDENCE_CONTRADICTED', 'INFERENCE', 'HYPOTHESIS', 'ALTERNATIVE_HYPOTHESIS', 'UNCERTAIN', 'DISPROVEN', 'RETRACTED');
CREATE TYPE alert_level AS ENUM ('BASELINE', 'ATTENTION', 'WARNING', 'DANGER', 'CRITICAL');
CREATE TYPE analysis_domain AS ENUM ('BIOLOGICAL_HEALTH', 'ENVIRONMENTAL_CLIMATE', 'VIOLENCE_ESCALATION', 'SOCIOLOGICAL_POLARIZATION', 'DISINFORMATION', 'INFLUENCE_PROPAGANDA', 'BORDER_GEOPOLITICAL', 'TERRITORIAL_INTEGRATED', 'INFRASTRUCTURE_SERVICES', 'ECONOMIC_SOCIAL');
CREATE TYPE source_type AS ENUM ('GOVERNMENT_OFFICIAL', 'GOVERNMENT_AGENCY', 'INTERNATIONAL_ORG', 'ACADEMIC_RESEARCH', 'NEWS_MEDIA', 'SOCIAL_MEDIA', 'NGO', 'THINK_TANK', 'CORPORATE', 'CITIZEN_REPORT', 'SENSOR_IOT', 'SATELLITE', 'HEALTH_SYSTEM', 'ENVIRONMENTAL_MONITOR', 'SECURITY_FORCE', 'BORDER_CONTROL', 'FINANCIAL_DATA', 'TELECOM_DATA', 'OTHER');
CREATE TYPE source_quality AS ENUM ('VERIFIED_HIGH', 'VERIFIED_MEDIUM', 'VERIFIED_LOW', 'UNVERIFIED', 'DISCREDITED', 'MALICIOUS');
CREATE TYPE source_independence AS ENUM ('PRIMARY', 'SECONDARY_INDEPENDENT', 'SECONDARY_DEPENDENT', 'TERTIARY', 'UNKNOWN');
CREATE TYPE document_type AS ENUM ('OFFICIAL_REPORT', 'SCIENTIFIC_PAPER', 'NEWS_ARTICLE', 'SOCIAL_MEDIA_POST', 'GOVERNMENT_DOCUMENT', 'LEGAL_DOCUMENT', 'HEALTH_RECORD', 'ENVIRONMENTAL_DATA', 'ECONOMIC_DATA', 'SECURITY_REPORT', 'BORDER_REPORT', 'SENSOR_DATA', 'SATELLITE_IMAGE', 'AUDIO_TRANSCRIPT', 'VIDEO_TRANSCRIPT', 'DATABASE_RECORD', 'API_RESPONSE', 'OTHER');
CREATE TYPE observation_type AS ENUM ('EVENT', 'STATE', 'TREND', 'ANOMALY', 'CORRELATION', 'CAUSATION', 'PREDICTION', 'RETRODICTION');
CREATE TYPE evidence_type AS ENUM ('DIRECT_OBSERVATION', 'DOCUMENTARY', 'STATISTICAL', 'EXPERT_TESTIMONY', 'PHYSICAL', 'DIGITAL', 'CIRCUMSTANTIAL', 'ANALOGICAL');
CREATE TYPE hypothesis_type AS ENUM ('EXPLANATORY', 'PREDICTIVE', 'CAUSAL', 'CORRELATIONAL', 'MECHANISTIC', 'STATISTICAL');
CREATE TYPE risk_type AS ENUM ('EXISTENTIAL', 'CATASTROPHIC', 'SEVERE', 'MODERATE', 'MINOR');
CREATE TYPE intervention_type AS ENUM ('INFORMATION_PUBLIC', 'EDUCATION', 'COMMUNITY_BUILDING', 'INSTITUTIONAL', 'POLICY', 'TECHNICAL', 'EMERGENCY', 'PREVENTIVE');
CREATE TYPE session_type AS ENUM ('VOLUNTARY_REFLECTION', 'EMOTIONAL_CHECK', 'STRESS_ASSESSMENT', 'WELLBEING_TRACKING');
CREATE TYPE medical_consultation_type AS ENUM ('GENERAL_INQUIRY', 'SYMPTOM_CHECK', 'PROFESSIONAL_CONSULTATION', 'FOLLOW_UP');
CREATE TYPE audit_action AS ENUM ('CREATE', 'READ', 'UPDATE', 'DELETE', 'EXPORT', 'IMPORT', 'LOGIN', 'LOGOUT', 'PERMISSION_CHANGE', 'SECURITY_EVENT', 'SYSTEM_EVENT', 'DATA_ACCESS', 'ALERT_TRIGGERED', 'MODEL_INFERENCE', 'RAG_QUERY', 'EXTERNAL_API_CALL');

-- Users is bootstrapped by 000_users.sql so sources may safely reference it.
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), email VARCHAR(255) NOT NULL, username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL, mfa_enabled BOOLEAN NOT NULL DEFAULT false, mfa_secret VARCHAR(255),
    full_name VARCHAR(255), role VARCHAR(100) NOT NULL DEFAULT 'CITIZEN', organization VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true, is_verified BOOLEAN NOT NULL DEFAULT false, last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0, locked_until TIMESTAMPTZ, password_changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT users_email_unique UNIQUE (email), CONSTRAINT users_username_unique UNIQUE (username)
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email); CREATE INDEX IF NOT EXISTS idx_users_role ON users(role); CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), name VARCHAR(500) NOT NULL, description TEXT, type source_type NOT NULL,
    quality source_quality NOT NULL DEFAULT 'UNVERIFIED', independence source_independence NOT NULL DEFAULT 'UNKNOWN',
    url VARCHAR(2048), official_name VARCHAR(500), country VARCHAR(100), region VARCHAR(100), language VARCHAR(10),
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), last_verified_at TIMESTAMPTZ, verified_by UUID REFERENCES users(id),
    domains analysis_domain[], tags TEXT[], is_active BOOLEAN NOT NULL DEFAULT true, is_blocked BOOLEAN NOT NULL DEFAULT false,
    blocked_reason TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT sources_name_unique UNIQUE (name), CONSTRAINT sources_url_unique UNIQUE (url)
);
CREATE INDEX idx_sources_type ON sources(type); CREATE INDEX idx_sources_quality ON sources(quality); CREATE INDEX idx_sources_domains ON sources USING GIN(domains); CREATE INDEX idx_sources_tags ON sources USING GIN(tags); CREATE INDEX idx_sources_active ON sources(is_active); CREATE INDEX idx_sources_name_trgm ON sources USING GIN(name gin_trgm_ops);

CREATE TABLE roles (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), name VARCHAR(100) NOT NULL UNIQUE, description TEXT, permissions JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE TABLE user_roles (user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE, granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), granted_by UUID REFERENCES users(id), expires_at TIMESTAMPTZ, PRIMARY KEY (user_id, role_id));

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT, type document_type NOT NULL,
    content_hash VARCHAR(64) NOT NULL, content_type VARCHAR(100), content_size_bytes BIGINT, language VARCHAR(10), source_id UUID NOT NULL REFERENCES sources(id),
    original_url VARCHAR(2048), published_at TIMESTAMPTZ, retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), domains analysis_domain[],
    epistemic_state epistemic_state NOT NULL DEFAULT 'DECLARATION', confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    storage_provider VARCHAR(50), storage_bucket VARCHAR(255), storage_key VARCHAR(500), storage_url VARCHAR(2048), processing_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    processed_at TIMESTAMPTZ, processing_error TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT documents_content_hash_unique UNIQUE (content_hash)
);
CREATE INDEX idx_documents_type ON documents(type); CREATE INDEX idx_documents_source ON documents(source_id); CREATE INDEX idx_documents_domains ON documents USING GIN(domains); CREATE INDEX idx_documents_epistemic ON documents(epistemic_state); CREATE INDEX idx_documents_processed ON documents(processing_status); CREATE INDEX idx_documents_created ON documents(created_at); CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);

CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT NOT NULL, text_hash VARCHAR(64) NOT NULL, start_offset INTEGER, end_offset INTEGER, page_number INTEGER,
    type observation_type NOT NULL, domains analysis_domain[], entities JSONB, keywords TEXT[], observed_at TIMESTAMPTZ,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    extraction_method VARCHAR(100), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT observations_text_hash_unique UNIQUE (text_hash)
);
CREATE INDEX idx_observations_document ON observations(document_id); CREATE INDEX idx_observations_type ON observations(type); CREATE INDEX idx_observations_domains ON observations USING GIN(domains); CREATE INDEX idx_observations_keywords ON observations USING GIN(keywords); CREATE INDEX idx_observations_observed_at ON observations(observed_at); CREATE INDEX idx_observations_text_trgm ON observations USING GIN(text gin_trgm_ops);

-- PostgreSQL cannot enforce element-wise foreign keys from UUID[] to UUID. Array relationships are stored as identifiers and must be validated by domain services before persistence.
CREATE TABLE evidences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT, type evidence_type NOT NULL,
    observation_ids UUID[] NOT NULL, quality_score DECIMAL(5,4) CHECK (quality_score >= 0 AND quality_score <= 1), independence_count INTEGER NOT NULL DEFAULT 1,
    corroboration_count INTEGER NOT NULL DEFAULT 0, contradiction_count INTEGER NOT NULL DEFAULT 0, is_corroborated BOOLEAN NOT NULL DEFAULT false,
    is_contradicted BOOLEAN NOT NULL DEFAULT false, domains analysis_domain[], created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT evidences_title_unique UNIQUE (title)
);
CREATE INDEX idx_evidences_type ON evidences(type); CREATE INDEX idx_evidences_domains ON evidences USING GIN(domains); CREATE INDEX idx_evidences_quality ON evidences(quality_score); CREATE INDEX idx_evidences_corroborated ON evidences(is_corroborated);

CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), text TEXT NOT NULL, text_hash VARCHAR(64) NOT NULL, title VARCHAR(500), epistemic_state epistemic_state NOT NULL DEFAULT 'DECLARATION',
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1), uncertainty_score DECIMAL(5,4) CHECK (uncertainty_score >= 0 AND uncertainty_score <= 1),
    supporting_evidence_ids UUID[], contradicting_evidence_ids UUID[], source_ids UUID[], document_ids UUID[], domains analysis_domain[],
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), trend VARCHAR(20), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT claims_text_hash_unique UNIQUE (text_hash)
);
CREATE INDEX idx_claims_epistemic ON claims(epistemic_state); CREATE INDEX idx_claims_domains ON claims USING GIN(domains); CREATE INDEX idx_claims_confidence ON claims(confidence_score); CREATE INDEX idx_claims_created ON claims(created_at); CREATE INDEX idx_claims_text_trgm ON claims USING GIN(text gin_trgm_ops);

CREATE TABLE hypotheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT NOT NULL, type hypothesis_type NOT NULL, status VARCHAR(50) NOT NULL DEFAULT 'PROPOSED',
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1), supporting_evidence_ids UUID[], contradicting_evidence_ids UUID[], explains_claim_ids UUID[],
    domains analysis_domain[], prior_probability DECIMAL(5,4), posterior_probability DECIMAL(5,4), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT hypotheses_title_unique UNIQUE (title)
);
CREATE INDEX idx_hypotheses_type ON hypotheses(type); CREATE INDEX idx_hypotheses_status ON hypotheses(status); CREATE INDEX idx_hypotheses_domains ON hypotheses USING GIN(domains); CREATE INDEX idx_hypotheses_confidence ON hypotheses(confidence_score);
CREATE TABLE competing_hypotheses (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), hypothesis_a_id UUID NOT NULL REFERENCES hypotheses(id) ON DELETE CASCADE, hypothesis_b_id UUID NOT NULL REFERENCES hypotheses(id) ON DELETE CASCADE, competition_type VARCHAR(50), notes TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), CONSTRAINT competing_hypotheses_unique UNIQUE (hypothesis_a_id, hypothesis_b_id));

CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT, type VARCHAR(100) NOT NULL, domains analysis_domain[],
    magnitude DECIMAL(10,4), velocity DECIMAL(10,4), acceleration DECIMAL(10,4), is_anomalous BOOLEAN NOT NULL DEFAULT false, anomaly_score DECIMAL(5,4), baseline_value DECIMAL(10,4),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), valid_from TIMESTAMPTZ, valid_until TIMESTAMPTZ, observation_ids UUID[], evidence_ids UUID[], created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT signals_title_unique UNIQUE (title)
);
CREATE INDEX idx_signals_type ON signals(type); CREATE INDEX idx_signals_domains ON signals USING GIN(domains); CREATE INDEX idx_signals_anomalous ON signals(is_anomalous); CREATE INDEX idx_signals_detected ON signals(detected_at); CREATE INDEX idx_signals_magnitude ON signals(magnitude);

CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), signal_id UUID NOT NULL REFERENCES signals(id), anomaly_type VARCHAR(100) NOT NULL, detection_method VARCHAR(100) NOT NULL,
    detection_score DECIMAL(5,4) NOT NULL, threshold DECIMAL(5,4), description TEXT NOT NULL, severity VARCHAR(20) NOT NULL, potential_impact TEXT, affected_domains analysis_domain[],
    status VARCHAR(50) NOT NULL DEFAULT 'DETECTED', confirmed_at TIMESTAMPTZ, confirmed_by UUID REFERENCES users(id), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT anomalies_signal_unique UNIQUE (signal_id)
);
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type); CREATE INDEX idx_anomalies_severity ON anomalies(severity); CREATE INDEX idx_anomalies_status ON anomalies(status); CREATE INDEX idx_anomalies_domains ON anomalies USING GIN(affected_domains);

CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT, type risk_type NOT NULL, domains analysis_domain[],
    probability DECIMAL(5,4) NOT NULL CHECK (probability >= 0 AND probability <= 1), impact DECIMAL(5,4) NOT NULL CHECK (impact >= 0 AND impact <= 5), vulnerability DECIMAL(5,4) CHECK (vulnerability >= 0 AND vulnerability <= 1), risk_score DECIMAL(5,4) NOT NULL,
    conditions JSONB, triggers TEXT[], evidence_ids UUID[], signal_ids UUID[], anomaly_ids UUID[], hypothesis_ids UUID[], assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), valid_from TIMESTAMPTZ, valid_until TIMESTAMPTZ, review_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id), CONSTRAINT risk_assessments_title_unique UNIQUE (title)
);
CREATE INDEX idx_risk_type ON risk_assessments(type); CREATE INDEX idx_risk_domains ON risk_assessments USING GIN(domains); CREATE INDEX idx_risk_score ON risk_assessments(risk_score); CREATE INDEX idx_risk_status ON risk_assessments(status);

CREATE TABLE risk_convergences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT, risk_assessment_ids UUID[] NOT NULL, domains analysis_domain[] NOT NULL,
    convergence_type VARCHAR(100), combined_risk_score DECIMAL(5,4) NOT NULL, amplification_factor DECIMAL(5,4), status VARCHAR(50) NOT NULL DEFAULT 'DETECTED', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT risk_convergences_title_unique UNIQUE (title)
);
CREATE INDEX idx_convergences_domains ON risk_convergences USING GIN(domains); CREATE INDEX idx_convergences_score ON risk_convergences(combined_risk_score);

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT NOT NULL, level alert_level NOT NULL, domains analysis_domain[] NOT NULL,
    risk_assessment_ids UUID[], convergence_ids UUID[], anomaly_ids UUID[], signal_ids UUID[], explanation TEXT, evidence_summary TEXT, recommended_actions TEXT[], intervention_types intervention_type[],
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), expires_at TIMESTAMPTZ, resolved_at TIMESTAMPTZ, status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', notifications_sent BOOLEAN NOT NULL DEFAULT false,
    notification_channels TEXT[], created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id), acknowledged_at TIMESTAMPTZ, acknowledged_by UUID REFERENCES users(id), CONSTRAINT alerts_title_unique UNIQUE (title)
);
CREATE INDEX idx_alerts_level ON alerts(level); CREATE INDEX idx_alerts_domains ON alerts USING GIN(domains); CREATE INDEX idx_alerts_status ON alerts(status); CREATE INDEX idx_alerts_triggered ON alerts(triggered_at);

CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT NOT NULL, scenario_type VARCHAR(100), domains analysis_domain[], assumptions TEXT[] NOT NULL,
    probability DECIMAL(5,4) CHECK (probability >= 0 AND probability <= 1), confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1), time_horizon VARCHAR(50), horizon_months INTEGER,
    valid_from TIMESTAMPTZ, valid_until TIMESTAMPTZ, risk_assessment_ids UUID[], hypothesis_ids UUID[], signal_ids UUID[], expected_impact TEXT, impact_severity risk_type, tracking_indicators TEXT[],
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id), CONSTRAINT scenarios_title_unique UNIQUE (title)
);
CREATE INDEX idx_scenarios_type ON scenarios(scenario_type); CREATE INDEX idx_scenarios_domains ON scenarios USING GIN(domains); CREATE INDEX idx_scenarios_probability ON scenarios(probability);

CREATE TABLE interventions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), title VARCHAR(500) NOT NULL, description TEXT, type intervention_type NOT NULL, domains analysis_domain[], alert_ids UUID[], risk_assessment_ids UUID[], actions TEXT[] NOT NULL,
    expected_outcome TEXT, success_metrics TEXT[], status VARCHAR(50) NOT NULL DEFAULT 'PROPOSED', proposed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), approved_at TIMESTAMPTZ, started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ,
    assigned_to UUID REFERENCES users(id), actual_outcome TEXT, effectiveness_score DECIMAL(5,4), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id), CONSTRAINT interventions_title_unique UNIQUE (title)
);
CREATE INDEX idx_interventions_type ON interventions(type); CREATE INDEX idx_interventions_status ON interventions(status); CREATE INDEX idx_interventions_domains ON interventions USING GIN(domains);

CREATE TABLE emotional_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), user_id UUID NOT NULL REFERENCES users(id), type session_type NOT NULL, content_hash VARCHAR(64), mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10), anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10), duration_minutes INTEGER, notes TEXT, is_completed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), completed_at TIMESTAMPTZ, CONSTRAINT emotional_sessions_user_check CHECK (user_id IS NOT NULL)
);
CREATE INDEX idx_emotional_sessions_user ON emotional_sessions(user_id); CREATE INDEX idx_emotional_sessions_type ON emotional_sessions(type); CREATE INDEX idx_emotional_sessions_created ON emotional_sessions(created_at);

CREATE TABLE medical_consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), user_id UUID NOT NULL REFERENCES users(id), professional_id UUID REFERENCES users(id), type medical_consultation_type NOT NULL, content_hash VARCHAR(64), symptoms JSONB,
    diagnosis TEXT, diagnosis_code VARCHAR(50), recommendations TEXT[], prescriptions TEXT[], referrals TEXT[], status VARCHAR(50) NOT NULL DEFAULT 'OPEN', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), closed_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id), is_encrypted BOOLEAN NOT NULL DEFAULT true, is_hipaa_compliant BOOLEAN NOT NULL DEFAULT true, CONSTRAINT medical_consultations_user_check CHECK (user_id IS NOT NULL)
);
CREATE INDEX idx_medical_consultations_user ON medical_consultations(user_id); CREATE INDEX idx_medical_consultations_professional ON medical_consultations(professional_id); CREATE INDEX idx_medical_consultations_status ON medical_consultations(status); CREATE INDEX idx_medical_consultations_created ON medical_consultations(created_at);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), action audit_action NOT NULL, entity_type VARCHAR(100), entity_id UUID, user_id UUID REFERENCES users(id), description TEXT, metadata JSONB, ip_address INET, user_agent TEXT,
    success BOOLEAN NOT NULL DEFAULT true, error_message TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_action ON audit_log(action); CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id); CREATE INDEX idx_audit_user ON audit_log(user_id); CREATE INDEX idx_audit_created ON audit_log(created_at); CREATE INDEX idx_audit_success ON audit_log(success);

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), document_id UUID REFERENCES documents(id) ON DELETE CASCADE, observation_id UUID REFERENCES observations(id) ON DELETE CASCADE, claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    embedding vector(1536), model_name VARCHAR(100) NOT NULL, model_version VARCHAR(50), dimensions INTEGER NOT NULL, chunk_index INTEGER, chunk_start INTEGER, chunk_end INTEGER, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT embeddings_entity_check CHECK ((document_id IS NOT NULL AND observation_id IS NULL AND claim_id IS NULL) OR (document_id IS NULL AND observation_id IS NOT NULL AND claim_id IS NULL) OR (document_id IS NULL AND observation_id IS NULL AND claim_id IS NOT NULL))
);
CREATE INDEX idx_embeddings_document ON embeddings(document_id); CREATE INDEX idx_embeddings_observation ON embeddings(observation_id); CREATE INDEX idx_embeddings_claim ON embeddings(claim_id); CREATE INDEX idx_embeddings_vector ON embeddings USING HNSW (embedding vector_cosine_ops);

CREATE TABLE rag_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), query_text TEXT NOT NULL, query_hash VARCHAR(64), result_document_ids UUID[], result_observation_ids UUID[], result_claim_ids UUID[], result_count INTEGER, top_k INTEGER, similarity_threshold DECIMAL(5,4),
    user_id UUID REFERENCES users(id), session_id VARCHAR(100), response_text TEXT, response_model VARCHAR(100), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id)
);
CREATE INDEX idx_rag_queries_user ON rag_queries(user_id); CREATE INDEX idx_rag_queries_created ON rag_queries(created_at);

CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), key VARCHAR(255) NOT NULL UNIQUE, value JSONB NOT NULL, description TEXT, config_type VARCHAR(50), scope VARCHAR(50), domain analysis_domain, is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id), CONSTRAINT system_config_key_unique UNIQUE (key)
);
CREATE INDEX idx_system_config_key ON system_config(key); CREATE INDEX idx_system_config_type ON system_config(config_type); CREATE INDEX idx_system_config_domain ON system_config(domain);

CREATE TABLE domain_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), domain analysis_domain NOT NULL UNIQUE, config JSONB NOT NULL, is_enabled BOOLEAN NOT NULL DEFAULT true, is_public BOOLEAN NOT NULL DEFAULT false, alert_thresholds JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id)
);
CREATE INDEX idx_domain_config_domain ON domain_config(domain); CREATE INDEX idx_domain_config_enabled ON domain_config(is_enabled);

CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), entity_a_type VARCHAR(100) NOT NULL, entity_a_id UUID NOT NULL, entity_b_type VARCHAR(100) NOT NULL, entity_b_id UUID NOT NULL, relationship_type VARCHAR(100) NOT NULL,
    strength DECIMAL(5,4) CHECK (strength >= 0 AND strength <= 1), confidence DECIMAL(5,4) CHECK (confidence >= 0 AND confidence <= 1), description TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), created_by UUID REFERENCES users(id),
    CONSTRAINT entity_relationships_unique UNIQUE (entity_a_type, entity_a_id, entity_b_type, entity_b_id, relationship_type)
);
CREATE INDEX idx_entity_relationships_a ON entity_relationships(entity_a_type, entity_a_id); CREATE INDEX idx_entity_relationships_b ON entity_relationships(entity_b_type, entity_b_id); CREATE INDEX idx_entity_relationships_type ON entity_relationships(relationship_type);

CREATE VIEW domain_epistemic_summary AS
SELECT domain, COUNT(*) as total_documents, COUNT(*) FILTER (WHERE epistemic_state = 'FACT_DOCUMENTED') as facts, COUNT(*) FILTER (WHERE epistemic_state = 'DECLARATION') as declarations,
       COUNT(*) FILTER (WHERE epistemic_state = 'EVIDENCE_SUPPORTED') as supported, COUNT(*) FILTER (WHERE epistemic_state = 'EVIDENCE_CONTRADICTED') as contradicted,
       COUNT(*) FILTER (WHERE epistemic_state = 'UNCERTAIN') as uncertain, AVG(confidence_score) as avg_confidence
FROM documents, UNNEST(domains) as domain GROUP BY domain;

CREATE VIEW active_alerts_summary AS
SELECT level, COUNT(*) as count, ARRAY_AGG(title) as titles FROM alerts WHERE status = 'ACTIVE' GROUP BY level
ORDER BY CASE level WHEN 'CRITICAL' THEN 1 WHEN 'DANGER' THEN 2 WHEN 'WARNING' THEN 3 WHEN 'ATTENTION' THEN 4 ELSE 5 END;

CREATE VIEW domain_risk_summary AS
SELECT domain, COUNT(*) as total_risks, AVG(risk_score) as avg_risk_score, MAX(risk_score) as max_risk_score,
       COUNT(*) FILTER (WHERE type = 'EXISTENTIAL') as existential_risks, COUNT(*) FILTER (WHERE type = 'CATASTROPHIC') as catastrophic_risks,
       COUNT(*) FILTER (WHERE status = 'ACTIVE') as active_risks
FROM risk_assessments, UNNEST(domains) as domain GROUP BY domain;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_evidences_updated_at BEFORE UPDATE ON evidences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_claims_updated_at BEFORE UPDATE ON claims FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hypotheses_updated_at BEFORE UPDATE ON hypotheses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_risk_assessments_updated_at BEFORE UPDATE ON risk_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON scenarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON interventions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_domain_config_updated_at BEFORE UPDATE ON domain_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO domain_config (domain, config, is_enabled, is_public, alert_thresholds) VALUES
('BIOLOGICAL_HEALTH', '{"monitoring_enabled": true, "data_sources": ["health_systems", "environmental_monitors"], "update_frequency": "daily"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),
('ENVIRONMENTAL_CLIMATE', '{"monitoring_enabled": true, "data_sources": ["satellites", "sensors", "government_reports"], "update_frequency": "hourly"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),
('VIOLENCE_ESCALATION', '{"monitoring_enabled": true, "data_sources": ["security_forces", "news_media", "social_media"], "update_frequency": "realtime"}'::jsonb, true, false, '{"attention": 0.2, "warning": 0.4, "danger": 0.6, "critical": 0.8}'::jsonb),
('SOCIOLOGICAL_POLARIZATION', '{"monitoring_enabled": true, "data_sources": ["social_media", "surveys", "academic_research"], "update_frequency": "daily"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.85}'::jsonb),
('DISINFORMATION', '{"monitoring_enabled": true, "data_sources": ["fact_checkers", "social_media", "news_media"], "update_frequency": "realtime"}'::jsonb, true, false, '{"attention": 0.25, "warning": 0.45, "danger": 0.65, "critical": 0.85}'::jsonb),
('INFLUENCE_PROPAGANDA', '{"monitoring_enabled": true, "data_sources": ["social_media", "think_tanks", "government_documents"], "update_frequency": "daily"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),
('BORDER_GEOPOLITICAL', '{"monitoring_enabled": true, "data_sources": ["border_control", "government_documents", "international_orgs"], "update_frequency": "daily"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),
('TERRITORIAL_INTEGRATED', '{"monitoring_enabled": true, "data_sources": ["all_domains"], "update_frequency": "hourly"}'::jsonb, true, false, '{"attention": 0.35, "warning": 0.55, "danger": 0.75, "critical": 0.9}'::jsonb),
('INFRASTRUCTURE_SERVICES', '{"monitoring_enabled": true, "data_sources": ["government_agencies", "sensors", "citizen_reports"], "update_frequency": "hourly"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb),
('ECONOMIC_SOCIAL', '{"monitoring_enabled": true, "data_sources": ["financial_data", "government_reports", "academic_research"], "update_frequency": "daily"}'::jsonb, true, false, '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb);

INSERT INTO system_config (key, value, description, config_type, scope) VALUES
('system.name', '"CEUTIA"', 'Nombre del sistema', 'STRING', 'GLOBAL'), ('system.version', '"2.0.0"', 'Versión del sistema', 'STRING', 'GLOBAL'), ('system.environment', '"development"', 'Entorno (development, staging, production)', 'STRING', 'GLOBAL'),
('ai.provider', '"openai"', 'Proveedor de IA', 'STRING', 'GLOBAL'), ('ai.model', '"gpt-4"', 'Modelo de IA por defecto', 'STRING', 'GLOBAL'), ('ai.temperature', '0.7', 'Temperatura por defecto', 'NUMBER', 'GLOBAL'),
('rag.top_k', '10', 'Número de resultados RAG', 'NUMBER', 'GLOBAL'), ('rag.similarity_threshold', '0.7', 'Umbral de similitud RAG', 'NUMBER', 'GLOBAL'), ('security.rate_limit', '100', 'Rate limit por minuto', 'NUMBER', 'GLOBAL'),
('security.max_login_attempts', '5', 'Máximos intentos de login', 'NUMBER', 'GLOBAL'), ('audit.enabled', 'true', 'Auditoría habilitada', 'BOOLEAN', 'GLOBAL'), ('medical_module.enabled', 'false', 'Módulo médico habilitado', 'BOOLEAN', 'GLOBAL');

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
