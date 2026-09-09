-- ============================================
-- CEUTIA — Initial Seed Data v2.0
-- ============================================
-- Propósito: Datos iniciales para arrancar el sistema
-- ============================================

-- ============================================
-- ROLES DEL SISTEMA
-- ============================================

INSERT INTO roles (id, name, description, permissions) VALUES
-- Rol: Administrador (Owner)
('00000000-0000-0000-0000-000000000001', 'OWNER', 
 'Administrador completo del sistema. Acceso total a todas las capas.',
 '{
   "public": ["read", "write", "delete"],
   "owner": ["read", "write", "delete", "admin"],
   "medical": ["read", "write", "delete", "admin"],
   "users": ["create", "read", "update", "delete"],
   "roles": ["create", "read", "update", "delete"],
   "config": ["create", "read", "update", "delete"],
   "audit": ["read"],
   "alerts": ["read", "write", "delete", "acknowledge"],
   "risks": ["read", "write", "delete"],
   "interventions": ["create", "read", "update", "delete", "approve"]
 }'::jsonb),

-- Rol: Analista (equipo interno)
('00000000-0000-0000-0000-000000000002', 'ANALYST',
 'Analista del equipo interno. Acceso a capa Owner para análisis.',
 '{
   "public": ["read", "write"],
   "owner": ["read", "write"],
   "medical": ["read"],
   "users": ["read"],
   "roles": ["read"],
   "config": ["read"],
   "audit": ["read"],
   "alerts": ["read", "acknowledge"],
   "risks": ["read", "write"],
   "interventions": ["read", "write"]
 }'::jsonb),

-- Rol: Profesional médico
('00000000-0000-0000-0000-000000000003', 'MEDICAL_PROFESSIONAL',
 'Profesional sanitario (Dr. Román). Acceso completo al módulo médico.',
 '{
   "public": ["read"],
   "owner": ["read"],
   "medical": ["read", "write", "delete", "admin"],
   "users": ["read"],
   "roles": ["read"],
   "config": ["read"],
   "audit": ["read"],
   "alerts": ["read"],
   "risks": ["read"],
   "interventions": ["read"]
 }'::jsonb),

-- Rol: Ciudadano (público general)
('00000000-0000-0000-0000-000000000004', 'CITIZEN',
 'Ciudadano. Acceso solo a capa pública.',
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
   "interventions": []
 }'::jsonb),

-- Rol: Investigador (acceso limitado)
('00000000-0000-0000-0000-000000000005', 'RESEARCHER',
 'Investigador externo. Acceso limitado para investigación.',
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
   "interventions": ["read"]
 }'::jsonb);

-- ============================================
-- USUARIO ADMINISTRADOR (OWNER)
-- ============================================

-- NOTA: La contraseña debe ser hasheada en producción
-- Este es un placeholder. Cambiar inmediatamente.
INSERT INTO users (id, email, username, password_hash, role, full_name, is_verified, is_active) VALUES
('00000000-0000-0000-0000-000000000001', 
 'owner@ceutia.system', 
 'owner', 
 '$2b$10$PLACEHOLDER_HASH_CHANGE_IMMEDIATELY', 
 'OWNER',
 'CEUTIA Administrator',
 true,
 true);

-- Asignar rol OWNER al usuario administrador
INSERT INTO user_roles (user_id, role_id) VALUES
('00000000-0000-0000-0000-000000000001', 
 '00000000-0000-0000-0000-000000000001');

-- ============================================
-- FUENTES AUTORIZADAS INICIALES
-- ============================================

INSERT INTO sources (id, name, type, quality, independence, description, domains) VALUES
-- Fuentes gubernamentales
('10000000-0000-0000-0000-000000000001', 
 'Gobierno de España - Portal oficial', 
 'GOVERNMENT_OFFICIAL', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Portal oficial del Gobierno de España',
 '["BORDER_GEOPOLITICAL", "INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL"]'),

('10000000-0000-0000-0000-000000000002', 
 'Junta de Andalucía', 
 'GOVERNMENT_AGENCY', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Gobierno de la Junta de Andalucía',
 '["INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL", "ENVIRONMENTAL_CLIMATE"]'),

('10000000-0000-0000-0000-000000000003', 
 'Ministerio del Interior - Seguridad', 
 'GOVERNMENT_AGENCY', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Ministerio del Interior (seguridad, fronteras)',
 '["VIOLENCE_ESCALATION", "BORDER_GEOPOLITICAL"]'),

-- Fuentes internacionales
('10000000-0000-0000-0000-000000000004', 
 'ONU - United Nations', 
 'INTERNATIONAL_ORG', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Organización de las Naciones Unidas',
 '["BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "ENVIRONMENTAL_CLIMATE"]'),

('10000000-0000-0000-0000-000000000005', 
 'UE - Unión Europea', 
 'INTERNATIONAL_ORG', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Unión Europea',
 '["BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES"]'),

-- Fuentes académicas
('10000000-0000-0000-0000-000000000006', 
 'Universidad de Cádiz - Ceuta', 
 'ACADEMIC_RESEARCH', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Campus de Ceuta de la Universidad de Cádiz',
 '["SOCIOLOGICAL_POLARIZATION", "ECONOMIC_SOCIAL", "BIOLOGICAL_HEALTH"]'),

('10000000-0000-0000-0000-000000000007', 
 'CSIC - Centro Superior de Investigaciones Científicas', 
 'ACADEMIC_RESEARCH', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Investigación científica en España',
 '["ENVIRONMENTAL_CLIMATE", "BIOLOGICAL_HEALTH", "ECONOMIC_SOCIAL"]'),

-- Medios de comunicación
('10000000-0000-0000-0000-000000000008', 
 'El País', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico español de referencia',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL"]'),

('10000000-0000-0000-0000-000000000009', 
 'El Mundo', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico español',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "VIOLENCE_ESCALATION"]'),

('10000000-0000-0000-0000-000000000010', 
 'Público', 
 'NEWS_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Periódico digital español',
 '["SOCIOLOGICAL_POLARIZATION", "BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL"]'),

-- Fuentes sanitarias
('10000000-0000-0000-0000-000000000011', 
 'Ministerio de Sanidad', 
 'HEALTH_SYSTEM', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Ministerio de Sanidad de España',
 '["BIOLOGICAL_HEALTH"]'),

('10000000-0000-0000-0000-000000000012', 
 'Servicio Andaluz de Salud', 
 'HEALTH_SYSTEM', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Servicio de salud de Andalucía (incluye Ceuta)',
 '["BIOLOGICAL_HEALTH"]'),

-- Fuentes ambientales
('10000000-0000-0000-0000-000000000013', 
 'AEMET - Agencia Estatal de Meteorología', 
 'ENVIRONMENTAL_MONITOR', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Agencia meteorológica oficial de España',
 '["ENVIRONMENTAL_CLIMATE"]'),

('10000000-0000-0000-0000-000000000014', 
 'MITECO - Medio Ambiente', 
 'ENVIRONMENTAL_MONITOR', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Ministerio para la Transición Ecológica',
 '["ENVIRONMENTAL_CLIMATE", "INFRASTRUCTURE_SERVICES"]'),

-- Think tanks
('10000000-0000-0000-0000-000000000015', 
 'CIDOB - Centro de Investigación y Documentación sobre Paz', 
 'THINK_TANK', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Investigación sobre paz y conflictos',
 '["VIOLENCE_ESCALATION", "BORDER_GEOPOLITICAL", "SOCIOLOGICAL_POLARIZATION"]'),

('10000000-0000-0000-0000-000000000016', 
 'FRIDE - Fundación para las Relaciones Internacionales', 
 'THINK_TANK', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Análisis de relaciones internacionales',
 '["BORDER_GEOPOLITICAL", "INFLUENCE_PROPAGANDA"]'),

-- ONGs
('10000000-0000-0000-0000-000000000017', 
 'Cruz Roja Española', 
 'NGO', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Organización humanitaria',
 '["BIOLOGICAL_HEALTH", "ECONOMIC_SOCIAL", "BORDER_GEOPOLITICAL"]'),

('10000000-0000-0000-0000-000000000018', 
 'CEAR - Comisión Española de Ayuda al Refugiado', 
 'NGO', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Ayuda a refugiados y migrantes',
 '["BORDER_GEOPOLITICAL", "ECONOMIC_SOCIAL", "SOCIOLOGICAL_POLARIZATION"]'),

-- Datos económicos
('10000000-0000-0000-0000-000000000019', 
 'INE - Instituto Nacional de Estadística', 
 'FINANCIAL_DATA', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Estadísticas oficiales de España',
 '["ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES"]'),

('10000000-0000-0000-0000-000000000020', 
 'Banco de España', 
 'FINANCIAL_DATA', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Banco central de España',
 '["ECONOMIC_SOCIAL"]'),

-- Control fronterizo
('10000000-0000-0000-0000-000000000021', 
 'Guardia Civil - Fronteras', 
 'BORDER_CONTROL', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Control fronterizo de la Guardia Civil',
 '["BORDER_GEOPOLITICAL", "VIOLENCE_ESCALATION"]'),

('10000000-0000-0000-0000-000000000022', 
 'Policía Nacional - Extranjería', 
 'BORDER_CONTROL', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Control de extranjería',
 '["BORDER_GEOPOLITICAL"]'),

-- Datos satelitales
('10000000-0000-0000-0000-000000000023', 
 'ESA - Agencia Espacial Europea', 
 'SATELLITE', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Datos satelitales de la ESA',
 '["ENVIRONMENTAL_CLIMATE", "INFRASTRUCTURE_SERVICES"]'),

('10000000-0000-0000-0000-000000000024', 
 'NASA - Earth Data', 
 'SATELLITE', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Datos satelitales de la NASA',
 '["ENVIRONMENTAL_CLIMATE"]'),

-- Redes sociales (monitorización)
('10000000-0000-0000-0000-000000000025', 
 'Twitter / X - API oficial', 
 'SOCIAL_MEDIA', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Datos de redes sociales (API)',
 '["SOCIOLOGICAL_POLARIZATION", "DISINFORMATION", "INFLUENCE_PROPAGANDA", "VIOLENCE_ESCALATION"]'),

-- Fact-checkers
('10000000-0000-0000-0000-000000000026', 
 'Maldita.es', 
 'NEWS_MEDIA', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Verificación de hechos (fact-checking)',
 '["DISINFORMATION", "INFLUENCE_PROPAGANDA"]'),

('10000000-0000-0000-0000-000000000027', 
 'Newtral', 
 'NEWS_MEDIA', 
 'VERIFIED_HIGH', 
 'SECONDARY_INDEPENDENT',
 'Verificación de hechos',
 '["DISINFORMATION", "INFLUENCE_PROPAGANDA"]'),

-- Seguridad
('10000000-0000-0000-0000-000000000028', 
 'Ministerio de Defensa', 
 'SECURITY_FORCE', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Fuerzas armadas de España',
 '["BORDER_GEOPOLITICAL", "VIOLENCE_ESCALATION"]'),

-- Datos de telecomunicaciones
('10000000-0000-0000-0000-000000000029', 
 'CNMC - Comisión Nacional de Mercados y Competencia', 
 'TELECOM_DATA', 
 'VERIFIED_HIGH', 
 'PRIMARY',
 'Datos de telecomunicaciones',
 '["INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL"]'),

-- Otras fuentes
('10000000-0000-0000-0000-000000000030', 
 'Observatorio Ceuta - Fuentes locales', 
 'OTHER', 
 'VERIFIED_MEDIUM', 
 'SECONDARY_INDEPENDENT',
 'Fuentes locales de Ceuta',
 '["SOCIOLOGICAL_POLARIZATION", "ECONOMIC_SOCIAL", "INFRASTRUCTURE_SERVICES", "VIOLENCE_ESCALATION"]');

-- ============================================
-- CONFIGURACIÓN ADICIONAL DEL SISTEMA
-- ============================================

-- Insertar fuentes por defecto para dominios
INSERT INTO system_config (key, value, description, config_type, scope) VALUES
('sources.default_count', '30', 'Número de fuentes autorizadas iniciales', 'NUMBER', 'GLOBAL'),
('domains.count', '10', 'Número de dominios de análisis', 'NUMBER', 'GLOBAL'),
('domains.enabled', 
 '["BIOLOGICAL_HEALTH", "ENVIRONMENTAL_CLIMATE", "VIOLENCE_ESCALATION", "SOCIOLOGICAL_POLARIZATION", "DISINFORMATION", "INFLUENCE_PROPAGANDA", "BORDER_GEOPOLITICAL", "TERRITORIAL_INTEGRATED", "INFRASTRUCTURE_SERVICES", "ECONOMIC_SOCIAL"]',
 'Dominios habilitados', 'JSON', 'GLOBAL'),
('epistemic.states', 
 '["FACT_DOCUMENTED", "DECLARATION", "EVIDENCE_SUPPORTED", "EVIDENCE_CONTRADICTED", "INFERENCE", "HYPOTHESIS", "ALTERNATIVE_HYPOTHESIS", "UNCERTAIN", "DISPROVEN", "RETRACTED"]',
 'Estados epistemológicos disponibles', 'JSON', 'GLOBAL'),
('alert.levels', 
 '["BASELINE", "ATTENTION", "WARNING", "DANGER", "CRITICAL"]',
 'Niveles de alerta', 'JSON', 'GLOBAL'),
('risk.types', 
 '["EXISTENTIAL", "CATASTROPHIC", "SEVERE", "MODERATE", "MINOR"]',
 'Tipos de riesgo', 'JSON', 'GLOBAL'),
('intervention.types', 
 '["INFORMATION_PUBLIC", "EDUCATION", "COMMUNITY_BUILDING", "INSTITUTIONAL", "POLICY", "TECHNICAL", "EMERGENCY", "PREVENTIVE"]',
 'Tipos de intervención (A-G)', 'JSON', 'GLOBAL');

-- ============================================
-- COMENTARIOS FINALES
-- ============================================

-- NOTA PARA EL ADMINISTRADOR:
-- 1. Cambiar la contraseña del usuario OWNER inmediatamente
-- 2. Habilitar MFA para el usuario OWNER
-- 3. Revisar y ajustar fuentes según necesidad
-- 4. Configurar dominios específicos de Ceuta
-- 5. Establecer umbrales de alerta específicos

-- ============================================
-- FIN DEL SEED DATA
-- ============================================
