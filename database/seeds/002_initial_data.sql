-- ============================================
-- CEUTIA — Initial Seed Data v2.0
-- ============================================
-- PROPÓSITO: Datos iniciales para arrancar el sistema
-- DOMINIOS: 10 (biológico, sanitario, ambiental, violencia, polarización, 
--            desinformación, influencia, fronterizo, territorial, infraestructuras)
-- ============================================
-- VERSIÓN: 2.0.0
-- ÚLTIMA ACTUALIZACIÓN: Septiembre 2026
-- ============================================

-- ============================================
-- NOTA IMPORTANTE
-- ============================================
-- Este archivo contiene datos iniciales CRÍTICOS.
-- Ejecutar SOLO una vez en fresh install.
-- Para producción, revisar y ajustar valores.
-- ============================================

-- ============================================
-- 1. ROLES DEL SISTEMA
-- ============================================

INSERT INTO roles (id, name, description, permissions) VALUES
-- Rol: Administrador (Owner)
('00000000-0000-0000-0000-000000000001', 'OWNER', 
 'Administrador completo del sistema. Acceso total a todas las capas (público, owner, médico).',
 '{
   "public": ["read", "write", "delete"],
   "owner": ["read", "write", "delete", "admin"],
   "medical": ["read", "write", "delete", "admin"],
   "users": ["create", "read", "update", "delete"],
   "roles": ["create", "read", "update", "delete"],
   "config": ["create", "read", "update", "delete"],
   "audit": ["read", "export"],
   "alerts": ["read", "write", "delete", "acknowledge", "resolve"],
   "risks": ["read", "write", "delete", "assess"],
   "interventions": ["create", "read", "update", "delete", "approve", "execute"],
   "sources": ["create", "read", "update", "delete", "verify"],
   "documents": ["create", "read", "update", "delete"],
   "hypotheses": ["create", "read", "update", "delete"],
   "scenarios": ["create", "read", "update", "delete"],
   "system": ["admin", "configure", "backup", "restore"]
 }'::jsonb),

-- Rol: Analista Senior (equipo interno)
('00000000-0000-0000-0000-000000000002', 'SENIOR_ANALYST',
 'Analista senior del equipo interno. Acceso completo a capa Owner para análisis avanzado.',
 '{
   "public": ["read", "write"],
   "owner": ["read", "write", "delete"],
   "medical": ["read"],
   "users": ["read"],
   "roles": ["read"],
   "config": ["read"],
   "audit": ["read"],
   "alerts": ["read", "write", "acknowledge"],
   "risks": ["read", "write", "assess"],
   "interventions": ["read", "write", "propose"],
   "sources": ["create", "read", "update", "verify"],
   "documents": ["create", "read", "update", "delete"],
   "hypotheses": ["create", "read", "update"],
   "scenarios": ["create", "read", "update"],
   "system": ["read"]
 }'::jsonb),

-- Rol: Analista Junior (equipo interno)
('00000000-0000-0000-0000-000000000003', 'JUNIOR_ANALYST',
 'Analista junior del equipo interno. Acceso limitado a capa Owner.',
 '{
   "public": ["read", "write"],
   "owner": ["read"],
   "medical": [],
   "users": [],
   "roles": [],
   "config": [],
   "audit": [],
   "alerts": ["read"],
   "risks": ["read"],
   "interventions": ["read"],
   "sources": ["read"],
   "documents": ["create", "read", "update"],
   "hypotheses": ["read"],
   "scenarios": ["read"],
   "system": []
 }'::jsonb),

-- Rol: Profesional Médico
('00000000-0000-0000-0000-000000000004', 'MEDICAL_PROFESSIONAL',
 'Profesional sanitario (Dr. Román). Acceso completo al módulo médico, limitado a Owner.',
 '{
   "public": ["read"],
   "owner": ["read"],
   "medical": ["read", "write", "delete", "admin", "diagnose", "prescribe"],
   "users": ["read"],
   "roles": [],
   "config": ["read"],
   "audit": ["read"],
   "alerts": ["read"],
   "risks": ["read"],
   "interventions": ["read"],
   "sources": ["read"],
   "documents": ["read"],
   "hypotheses": ["read"],
   "scenarios": ["read"],
   "system": []
 }'::jsonb),

-- Rol: Ciudadano (público general)
('00000000-0000-0000-0000-000000000005', 'CITIZEN',
 'Ciudadano. Acceso solo a capa pública y módulo emocional voluntario.',
 '{
   "public": ["read"],
   "owner": [],
   "medical": ["read", "write"],
   "users": ["read"],
   "roles": [],
   "config": ["read"],
   "audit": [],
   "alerts": ["read"],
   "risks": [],
   "interventions": [],
   "sources": ["read"],
   "documents": ["read"],
   "hypotheses": [],
   "scenarios": [],
   "system": []
 }'::jsonb),

-- Rol: Investigador (acceso limitado externo)
('00000000-0000-0000-0000-000000000006', 'RESEARCHER',
 'Investigador externo acreditado. Acceso de lectura a Owner para investigación.',
 '{
   "public": ["read"],
   "owner": ["read"],
   "medical": [],
   "users": [],
   "roles": [],
   "config": ["read"],
   "audit": [],
   "alerts": ["read"],
   "risks": ["read"],
   "interventions": ["read"],
   "sources": ["read"],
   "documents": ["read"],
   "hypotheses": ["read"],
   "scenarios": ["read"],
   "system": []
 }'::jsonb),

-- Rol: Periodista (acceso limitado)
('00000000-0000-0000-0000-000000000007', 'JOURNALIST',
 'Periodista acreditado. Acceso de lectura para verificación de hechos.',
 '{
   "public": ["read"],
   "owner": ["read"],
   "medical": [],
   "users": [],
   "roles": [],
   "config": [],
   "audit": [],
   "alerts": ["read"],
   "risks": ["read"],
   "interventions": [],
   "sources": ["read"],
   "documents": ["read"],
   "hypotheses": [],
   "scenarios": [],
   "system": []
 }'::jsonb),

-- Rol: Gobierno (acceso especial)
('00000000-0000-0000-0000-000000000008', 'GOVERNMENT_LIAISON',
 'Enlace gubernamental. Acceso limitado para coordinación institucional.',
 '{
   "public": ["read"],
   "owner": ["read"],
   "medical": [],
   "users": [],
   "roles": [],
   "config": [],
   "audit": [],
   "alerts": ["read"],
   "risks": ["read"],
   "interventions": ["read"],
   "sources": ["read"],
   "documents": ["read"],
   "hypotheses": [],
   "scenarios": ["read"],
   "system": []
 }'::jsonb);

-- ============================================
-- 2. USUARIO ADMINISTRADOR (OWNER)
-- ============================================

-- NOTA: La contraseña debe ser hasheada en producción
-- Este es un placeholder. CAMBIAR INMEDIATAMENTE después del primer login.
INSERT INTO users (id, email, username, password_hash, full_name, is_verified, is_active, created_at) VALUES
('00000000-0000-0000-0000-000000000001', 
 'owner@ceutia.system', 
 'owner', 
 '$2b$10$PLACEHOLDER_HASH_CHANGE_IMMEDIATELY_USE_BCRYPT', 
 'CEUTIA System Administrator',
 true,
 true,
 NOW());

-- Asignar rol OWNER al usuario administrador
INSERT INTO user_roles (user_id, role_id, granted_by) VALUES
('00000000-0000-0000-0000-000000000001', 
 '00000000-0000-0000-0000-000000000001',
 '00000000-0000-0000-0000-000000000001');

-- ============================================
-- 3. CONFIGURACIÓN DE DOMINIOS (10 DOMINIOS)
-- ============================================

-- Dominio 1: Biológico y Sanitario
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000001', 'BIOLOGICAL_HEALTH',
 '{
   "monitoring_enabled": true,
   "data_sources": ["health_systems", "environmental_monitors", "satellites", "government_reports"],
   "update_frequency": "hourly",
   "priority": "high",
   "indicators": [
     "mortality_rate",
     "morbidity_rate",
     "hospital_occupancy",
     "icu_occupancy",
     "emergency_visits",
     "pathogen_detection",
     "vaccination_coverage",
     "antibiotic_resistance",
     "environmental_contaminants",
     "water_quality",
     "air_quality_health_impact"
   ],
   "thresholds": {
     "mortality_anomaly": 1.5,
     "hospital_saturation": 0.85,
     "icu_saturation": 0.9,
     "pathogen_alert": true
   }
 }'::jsonb,
 true,
 false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb,
 NOW());

-- Dominio 2: Ambiental y Climático
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000002', 'ENVIRONMENTAL_CLIMATE',
 '{
   "monitoring_enabled": true,
   "data_sources": ["satellites", "sensors", "government_reports", "academic_research"],
   "update_frequency": "hourly",
   "priority": "high",
   "indicators": [
     "temperature_anomaly",
     "precipitation_anomaly",
     "drought_index",
     "fire_risk",
     "flood_risk",
     "air_quality_index",
     "water_quality",
     "soil_moisture",
     "vegetation_health",
     "sea_level",
     "extreme_weather_events"
   ],
   "thresholds": {
     "temperature_anomaly": 2.0,
     "fire_risk_extreme": true,
     "flood_risk_high": true,
     "aqi_unhealthy": 150
   }
 }'::jsonb,
 true,
 true,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb,
 NOW());

-- Dominio 3: Violencia y Escalada
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000003', 'VIOLENCE_ESCALATION',
 '{
   "monitoring_enabled": true,
   "data_sources": ["security_forces", "news_media", "social_media", "citizen_reports"],
   "update_frequency": "realtime",
   "priority": "critical",
   "indicators": [
     "violent_incidents",
     "threats_documented",
     "weapons_presence",
     "group_mobilization",
     "reciprocity_events",
     "contagion_effects",
     "capability_assessment",
     "opportunity_assessment",
     "escalation_trajectory",
     "dehumanization_language",
     "hate_speech_frequency"
   ],
   "thresholds": {
     "incidents_per_week": 5,
     "threats_critical": 3,
     "mobilization_large": 100,
     "escalation_rapid": true
   }
 }'::jsonb,
 true,
 false,
 '{"attention": 0.2, "warning": 0.4, "danger": 0.6, "critical": 0.8}'::jsonb,
 NOW());

-- Dominio 4: Polarización Sociológica
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000004', 'SOCIOLOGICAL_POLARIZATION',
 '{
   "monitoring_enabled": true,
   "data_sources": ["social_media", "surveys", "academic_research", "news_media"],
   "update_frequency": "daily",
   "priority": "high",
   "indicators": [
     "intergroup_hostility",
     "dehumanization_frequency",
     "discursive_segregation",
     "bridge_loss",
     "antagonistic_narratives",
     "position_concentration",
     "extremist_positions",
     "echo_chamber_strength",
     "affective_polarization",
     "perceived_threat"
   ],
   "thresholds": {
     "hostility_index": 0.6,
     "dehumanization_rate": 0.3,
     "segregation_index": 0.7,
     "extremist_concentration": 0.4
   }
 }'::jsonb,
 true,
 false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.85}'::jsonb,
 NOW());

-- Dominio 5: Desinformación
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000005', 'DISINFORMATION',
 '{
   "monitoring_enabled": true,
   "data_sources": ["fact_checkers", "social_media", "news_media", "government_reports"],
   "update_frequency": "realtime",
   "priority": "high",
   "indicators": [
     "false_claims_verified",
     "misleading_content",
     "fabricated_stories",
     "manipulated_media",
     "impersonation_attempts",
     "coordination_detected",
     "amplification_artificial",
     "emotional_targeting",
     "viral_velocity",
     "reach_estimate"
   ],
   "thresholds": {
     "false_claims_per_day": 10,
     "viral_threshold": 10000,
     "coordination_accounts": 5,
     "amplification_factor": 10
   }
 }'::jsonb,
 true,
 true,
 '{"attention": 0.25, "warning": 0.45, "danger": 0.65, "critical": 0.85}'::jsonb,
 NOW());

-- Dominio 6: Influencia y Propaganda
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000006', 'INFLUENCE_PROPAGANDA',
 '{
   "monitoring_enabled": true,
   "data_sources": ["social_media", "think_tanks", "government_documents", "news_media"],
   "update_frequency": "daily",
   "priority": "medium",
   "indicators": [
     "narrative_instrumentalization",
     "emotional_exploitation",
     "coordination_observable",
     "inauthentic_accounts",
     "echo_chambers_artificial",
     "amplification_patterns",
     "messaging_synchronization",
     "bot_network_detection",
     "troll_activity",
     "state_sponsored_indicators"
   ],
   "thresholds": {
     "coordination_score": 0.7,
     "inauthentic_percentage": 0.2,
     "amplification_anomaly": 5,
     "synchronization_index": 0.8
   }
 }'::jsonb,
 true,
 false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb,
 NOW());

-- Dominio 7: Fronterizo y Geopolítico
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000007', 'BORDER_GEOPOLITICAL',
 '{
   "monitoring_enabled": true,
   "data_sources": ["border_control", "government_documents", "international_orgs", "news_media"],
   "update_frequency": "daily",
   "priority": "high",
   "indicators": [
     "border_incidents",
     "regulatory_changes",
     "diplomatic_activity",
     "official_communications",
     "migration_pressure",
     "cooperation_changes",
     "tension_indicators",
     "military_activity",
     "intelligence_reports",
     "geopolitical_events"
   ],
   "thresholds": {
     "incidents_per_week": 10,
     "migration_surge": true,
     "tension_elevated": true,
     "diplomatic_crisis": true
   }
 }'::jsonb,
 true,
 false,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb,
 NOW());

-- Dominio 8: Territorial Integrado
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000008', 'TERRITORIAL_INTEGRATED',
 '{
   "monitoring_enabled": true,
   "data_sources": ["all_domains"],
   "update_frequency": "hourly",
   "priority": "critical",
   "indicators": [
     "cross_domain_convergences",
     "compound_anomalies",
     "weak_signals_amplified",
     "systemic_patterns",
     "domino_effects",
     "tipping_points",
     "cascading_failures",
     "interdependencies",
     "feedback_loops",
     "emergent_behaviors"
   ],
   "thresholds": {
     "convergence_count": 3,
     "anomaly_compound": true,
     "cascade_risk": true,
     "tipping_point_proximity": 0.8
   }
 }'::jsonb,
 true,
 false,
 '{"attention": 0.35, "warning": 0.55, "danger": 0.75, "critical": 0.9}'::jsonb,
 NOW());

-- Dominio 9: Infraestructuras y Servicios
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000009', 'INFRASTRUCTURE_SERVICES',
 '{
   "monitoring_enabled": true,
   "data_sources": ["government_agencies", "sensors", "citizen_reports", "utility_companies"],
   "update_frequency": "hourly",
   "priority": "high",
   "indicators": [
     "water_supply",
     "electricity_supply",
     "transport_disruptions",
     "education_disruptions",
     "healthcare_capacity",
     "security_public",
     "waste_management",
     "telecommunications",
     "fuel_supply",
     "food_supply"
   ],
   "thresholds": {
     "water_disruption_hours": 24,
     "electricity_outage_percentage": 0.1,
     "transport_severe": true,
     "healthcare_saturation": 0.9
   }
 }'::jsonb,
 true,
 true,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb,
 NOW());

-- Dominio 10: Económico y Social
INSERT INTO domain_config (id, domain, config, is_enabled, is_public, alert_thresholds, created_at) VALUES
('d0000000-0000-0000-0000-000000000010', 'ECONOMIC_SOCIAL',
 '{
   "monitoring_enabled": true,
   "data_sources": ["financial_data", "government_reports", "academic_research", "news_media"],
   "update_frequency": "daily",
   "priority": "medium",
   "indicators": [
     "economic_stress",
     "unemployment_rate",
     "housing_affordability",
     "food_security",
     "inequality_index",
     "psychological_wellbeing",
     "poverty_rate",
     "inflation_impact",
     "business_closures",
     "social_unrest_indicators"
   ],
   "thresholds": {
     "unemployment_critical": 0.2,
     "housing_stress": 0.4,
     "food_insecurity": 0.15,
     "inequality_gini": 0.5
   }
 }'::jsonb,
 true,
 true,
 '{"attention": 0.3, "warning": 0.5, "danger": 0.7, "critical": 0.9}'::jsonb,
 NOW());

-- ============================================
-- 4. CONFIGURACIÓN DEL SISTEMA
-- ============================================

INSERT INTO system_config (key, value, description, config_type, scope, created_at) VALUES
-- Sistema
('system.name', '"CEUTIA"', 'Nombre oficial del sistema', 'STRING', 'GLOBAL', NOW()),
('system.version', '"2.0.0"', 'Versión actual del sistema', 'STRING', 'GLOBAL', NOW()),
('system.environment', '"development"', 'Entorno de ejecución', 'STRING', 'GLOBAL', NOW()),
('system.timezone', '"Europe/Madrid"', 'Zona horaria del sistema', 'STRING', 'GLOBAL', NOW()),
('system.locale', '"es-ES"', 'Locale por defecto', 'STRING', 'GLOBAL', NOW()),

-- Dominios
('domains.count', '10', 'Número total de dominios de análisis', 'NUMBER', 'GLOBAL', NOW()),
('domains.enabled', 
 '["BIOLOGICAL_HEALTH", "ENVIRONMENTAL_CLIMATE", "VIOLENCE_ESCALATION", "SOCIOLOGICAL_POLARIZATION", "DISINFORMATION", "INFLUENCE_PROPAGANDA", "BORDER_GEOPOLITICAL", "TERRITORIAL_INTEGRATED", "INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL"]',
 'Lista de dominios habilitados', 'JSON', 'GLOBAL', NOW()),

-- Epistemología
('epistemic.states', 
 '["FACT_DOCUMENTED", "DECLARATION", "EVIDENCE_SUPPORTED", "EVIDENCE_CONTRADICTED", "INFERENCE", "HYPOTHESIS", "ALTERNATIVE_HYPOTHESIS", "UNCERTAIN", "DISPROVEN", "RETRACTED"]',
 'Estados epistemológicos disponibles', 'JSON', 'GLOBAL', NOW()),
('epistemic.confidence_min', '0.5', 'Confianza mínima para considerar algo como hecho', 'NUMBER', 'GLOBAL', NOW()),

-- Alertas
('alert.levels', 
 '["BASELINE", "ATTENTION", "WARNING", "DANGER", "CRITICAL"]',
 'Niveles de alerta disponibles', 'JSON', 'GLOBAL', NOW()),
('alert.auto_trigger', 'true', 'Activar alertas automáticamente', 'BOOLEAN', 'GLOBAL', NOW()),
('alert.notification_channels', '["email", "telegram"]', 'Canales de notificación por defecto', 'JSON', 'GLOBAL', NOW()),

-- Riesgos
('risk.types', 
 '["EXISTENTIAL", "CATASTROPHIC", "SEVERE", "MODERATE", "MINOR"]',
 'Tipos de riesgo disponibles', 'JSON', 'GLOBAL', NOW()),
('risk.assessment_frequency', '"daily"', 'Frecuencia de evaluación de riesgos', 'STRING', 'GLOBAL', NOW()),

-- Intervenciones
('intervention.types', 
 '["INFORMATION_PUBLIC", "EDUCATION", "COMMUNITY_BUILDING", "INSTITUTIONAL", "POLICY", "TECHNICAL", "EMERGENCY", "PREVENTIVE"]',
 'Tipos de intervención disponibles (A-G)', 'JSON', 'GLOBAL', NOW()),

-- IA
('ai.enabled', 'true', 'IA habilitada', 'BOOLEAN', 'GLOBAL', NOW()),
('ai.provider', '"openai"', 'Proveedor de IA por defecto', 'STRING', 'GLOBAL', NOW()),
('ai.model', '"gpt-4"', 'Modelo de IA por defecto', 'STRING', 'GLOBAL', NOW()),
('ai.temperature', '0.7', 'Temperatura por defecto', 'NUMBER', 'GLOBAL', NOW()),
('ai.max_tokens', '2000', 'Máximo tokens por defecto', 'NUMBER', 'GLOBAL', NOW()),

-- RAG
('rag.enabled', 'true', 'RAG habilitado', 'BOOLEAN', 'GLOBAL', NOW()),
('rag.top_k', '10', 'Número de resultados RAG por defecto', 'NUMBER', 'GLOBAL', NOW()),
('rag.similarity_threshold', '0.7', 'Umbral de similitud RAG', 'NUMBER', 'GLOBAL', NOW()),

-- Seguridad
('security.rate_limit', '100', 'Rate limit por minuto', 'NUMBER', 'GLOBAL', NOW()),
('security.max_login_attempts', '5', 'Máximos intentos de login', 'NUMBER', 'GLOBAL', NOW()),
('security.lockout_duration', '900000', 'Duración de lockout en ms (15 min)', 'NUMBER', 'GLOBAL', NOW()),
('security.mfa_required', 'false', 'MFA requerido para todos', 'BOOLEAN', 'GLOBAL', NOW()),
('security.mfa_required_roles', '["OWNER", "SENIOR_ANALYST"]', 'Roles que requieren MFA', 'JSON', 'GLOBAL', NOW()),

-- Auditoría
('audit.enabled', 'true', 'Auditoría habilitada', 'BOOLEAN', 'GLOBAL', NOW()),
('audit.retention_days', '365', 'Días de retención de auditoría', 'NUMBER', 'GLOBAL', NOW()),

-- Módulo médico
('medical.enabled', 'false', 'Módulo médico habilitado', 'BOOLEAN', 'GLOBAL', NOW()),
('medical.hipaa_compliant', 'true', 'Cumplimiento HIPAA', 'BOOLEAN', 'GLOBAL', NOW()),
('medical.gdpr_compliant', 'true', 'Cumplimiento GDPR', 'BOOLEAN', 'GLOBAL', NOW()),

-- Feature flags
('feature.public_web', 'true', 'Frontend público habilitado', 'BOOLEAN', 'GLOBAL', NOW()),
('feature.owner_radar', 'true', 'Radar Owner habilitado', 'BOOLEAN', 'GLOBAL', NOW()),
('feature.medical_module', 'false', 'Módulo médico habilitado', 'BOOLEAN', 'GLOBAL', NOW()),
('feature.ai_responses', 'true', 'Respuestas con IA habilitadas', 'BOOLEAN', 'GLOBAL', NOW()),
('feature.rag', 'true', 'RAG habilitado', 'BOOLEAN', 'GLOBAL', NOW()),
('feature.alerts_auto', 'true', 'Alertas automáticas habilitadas', 'BOOLEAN', 'GLOBAL', NOW()),
('feature.analytics', 'true', 'Analytics habilitado', 'BOOLEAN', 'GLOBAL', NOW());

-- ============================================
-- 5. FUENTES AUTORIZADAS (30+ FUENTES)
-- ============================================

-- Fuentes gubernamentales España
INSERT INTO sources (id, name, type, quality, independence, description, domains, is_active, created_at) VALUES
('s0000000-0000-0000-0000-000000000001', 
 'Gobierno de España - Portal oficial', 
 'GOVERNMENT_OFFICIAL', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Portal oficial del Gobierno de España (www.lamoncloa.com, www.gob.es)',
 '["BORDER_GEOPOLITICAL", "INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000002', 
 'Junta de Andalucía - Gobierno regional', 
 'GOVERNMENT_AGENCY', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Gobierno de la Junta de Andalucía (www.juntadeandalucia.es)',
 '["INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL", "ENVIRONMENTAL_CLIMATE", "BIOLOGICAL_HEALTH"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000003', 
 'Ministerio del Interior - Seguridad', 
 'GOVERNMENT_AGENCY', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Ministerio del Interior (seguridad, fronteras, www.interior.gob.es)',
 '["VIOLENCE_ESCALATION", "BORDER_GEOPOLITICAL", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000004', 
 'Ministerio de Sanidad', 
 'GOVERNMENT_AGENCY', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Ministerio de Sanidad (www.sanidad.gob.es)',
 '["BIOLOGICAL_HEALTH", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000005', 
 'Ministerio para la Transición Ecológica (MITECO)', 
 'GOVERNMENT_AGENCY', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Ministerio para la Transición Ecológica (www.miteco.gob.es)',
 '["ENVIRONMENTAL_CLIMATE", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

-- Fuentes internacionales
('s0000000-0000-0000-0000-000000000006', 
 'ONU - United Nations', 
 'INTERNATIONAL_ORG', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Organización de las Naciones Unidas (www.un.org)',
 '["BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "ENVIRONMENTAL_CLIMATE", "BIOLOGICAL_HEALTH"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000007', 
 'UE - Unión Europea', 
 'INTERNATIONAL_ORG', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Unión Europea (www.europa.eu)',
 '["BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES", "ENVIRONMENTAL_CLIMATE"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000008', 
 'OMS - Organización Mundial de la Salud', 
 'INTERNATIONAL_ORG', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Organización Mundial de la Salud (www.who.int)',
 '["BIOLOGICAL_HEALTH"]',
 true, NOW()),

-- Fuentes académicas
('s0000000-0000-0000-0000-000000000009', 
 'Universidad de Cádiz - Campus de Ceuta', 
 'ACADEMIC_RESEARCH', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Campus de Ceuta de la Universidad de Cádiz (www.uca.es/ceuta)',
 '["SOCIOLOGICAL_POLARIZATION", "ECONOMIC_SOCIAL", "BIOLOGICAL_HEALTH", "BORDER_GEOPOLITICAL"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000010', 
 'CSIC - Centro Superior de Investigaciones Científicas', 
 'ACADEMIC_RESEARCH', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Investigación científica en España (www.csic.es)',
 '["ENVIRONMENTAL_CLIMATE", "BIOLOGICAL_HEALTH", "ECONOMIC_SOCIAL"]',
 true, NOW()),

-- Medios de comunicación (España)
('s0000000-0000-0000-0000-000000000011', 
 'El País', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico español de referencia (elpais.com)',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "VIOLENCE_ESCALATION"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000012', 
 'El Mundo', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico español (elmundo.es)',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "VIOLENCE_ESCALATION", "ECONOMIC_SOCIAL"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000013', 
 'Público', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico digital español (publico.es)',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000014', 
 'ABC', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico español (abc.es)',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL"]',
 true, NOW()),

-- Medios locales Ceuta
('s0000000-0000-0000-0000-000000000015', 
 'Ceuta Tv', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Televisión local de Ceuta (ceutatv.es)',
 '["SOCIOLOGICAL_POLARIZATION", "ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES", "VIOLENCE_ESCALATION"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000016', 
 'El Faro de Ceuta', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico local de Ceuta (elfarodeceuta.es)',
 '["SOCIOLOGICAL_POLARIZATION", "ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES", "BORDER_GEOPOLITICAL"]',
 true, NOW()),

-- Fuentes sanitarias
('s0000000-0000-0000-0000-000000000017', 
 'Servicio Andaluz de Salud', 
 'HEALTH_SYSTEM', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Servicio de salud de Andalucía (incluye Ceuta) (www.sspa.juntadeandalucia.es)',
 '["BIOLOGICAL_HEALTH", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000018', 
 'Hospital Universitario de Ceuta', 
 'HEALTH_SYSTEM', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Hospital de Ceuta',
 '["BIOLOGICAL_HEALTH", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

-- Fuentes ambientales
('s0000000-0000-0000-0000-000000000019', 
 'AEMET - Agencia Estatal de Meteorología', 
 'ENVIRONMENTAL_MONITOR', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Agencia meteorológica oficial de España (www.aemet.es)',
 '["ENVIRONMENTAL_CLIMATE"]',
 true, NOW()),

-- Think tanks
('s0000000-0000-0000-0000-000000000020', 
 'CIDOB - Centro de Investigación y Documentación sobre Paz', 
 'THINK_TANK', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Investigación sobre paz y conflictos (www.cidob.org)',
 '["VIOLENCE_ESCALATION", "BORDER_GEOPOLITICAL", "SOCIOLOGICAL_POLARIZATION"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000021', 
 'FRIDE - Fundación para las Relaciones Internacionales', 
 'THINK_TANK', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Análisis de relaciones internacionales (www.fride.org)',
 '["BORDER_GEOPOLITICAL", "INFLUENCE_PROPAGANDA"]',
 true, NOW()),

-- ONGs
('s0000000-0000-0000-0000-000000000022', 
 'Cruz Roja Española', 
 'NGO', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Organización humanitaria (www.cruzroja.es)',
 '["BIOLOGICAL_HEALTH", "ECONOMIC_SOCIAL", "BORDER_GEOPOLITICAL", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000023', 
 'CEAR - Comisión Española de Ayuda al Refugiado', 
 'NGO', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Ayuda a refugiados y migrantes (www.cear.es)',
 '["BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "SOCIOLOGICAL_POLARIZATION", "BIOLOGICAL_HEALTH"]',
 true, NOW()),

-- Datos económicos
('s0000000-0000-0000-0000-000000000024', 
 'INE - Instituto Nacional de Estadística', 
 'FINANCIAL_DATA', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Estadísticas oficiales de España (www.ine.es)',
 '["ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES", "BIOLOGICAL_HEALTH"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000025', 
 'Banco de España', 
 'FINANCIAL_DATA', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Banco central de España (www.bde.es)',
 '["ECONOMIC_SOCIAL"]',
 true, NOW()),

-- Control fronterizo
('s0000000-0000-0000-0000-000000000026', 
 'Guardia Civil - Fronteras', 
 'BORDER_CONTROL', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Control fronterizo de la Guardia Civil',
 '["BORDER_GEOPOLITICAL", "VIOLENCE_ESCALATION"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000027', 
 'Policía Nacional - Extranjería', 
 'BORDER_CONTROL', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Control de extranjería',
 '["BORDER_GEOPOLITICAL"]',
 true, NOW()),

-- Datos satelitales
('s0000000-0000-0000-0000-000000000028', 
 'ESA - Agencia Espacial Europea', 
 'SATELLITE', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Datos satelitales de la ESA (www.esa.int)',
 '["ENVIRONMENTAL_CLIMATE", "INFRASTRUCTURE_SERVICES"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000029', 
 'NASA - Earth Data', 
 'SATELLITE', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Datos satelitales de la NASA (earthdata.nasa.gov)',
 '["ENVIRONMENTAL_CLIMATE"]',
 true, NOW()),

-- Fact-checkers
('s0000000-0000-0000-0000-000000000030', 
 'Maldita.es', 
 'NEWS_MEDIA', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Verificación de hechos (maldita.es)',
 '["DISINFORMATION", "INFLUENCE_PROPAGANDA"]',
 true, NOW()),

('s0000000-0000-0000-0000-000000000031', 
 'Newtral', 
 'NEWS_MEDIA', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Verificación de hechos (newtral.es)',
 '["DISINFORMATION", "INFLUENCE_PROPAGANDA"]',
 true, NOW()),

-- Seguridad
('s0000000-0000-0000-0000-000000000032', 
 'Ministerio de Defensa', 
 'SECURITY_FORCE', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Fuerzas armadas de España (www.defensa.gob.es)',
 '["BORDER_GEOPOLITICAL", "VIOLENCE_ESCALATION"]',
 true, NOW());

-- ============================================
-- COMENTARIOS FINALES
-- ============================================

-- NOTA PARA EL ADMINISTRADOR:
-- 1. Cambiar la contraseña del usuario OWNER inmediatamente
-- 2. Habilitar MFA para el usuario OWNER
-- 3. Revisar y ajustar fuentes según necesidad
-- 4. Configurar dominios específicos de Ceuta
-- 5. Establecer umbrales de alerta específicos
-- 6. Añadir más fuentes según sea necesario
-- 7. Configurar integración con APIs reales

-- ============================================
-- FIN DEL SEED DATA
-- ============================================
