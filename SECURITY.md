
# Política de Seguridad del Sistema CEUTIA

> **Política de seguridad de nivel estratégico para proteger infraestructura crítica de inteligencia territorial**
>
> *Clasificación: RESTRINGIDO*
> *Sistema de Inteligencia Territorial para Salvar a la Humanidad*

---

## 🎯 Propósito Estratégico

Esta política establece controles de seguridad de **nivel militar/inteligencia** para proteger:

- **Infraestructura crítica** — Sistema de alerta temprana territorial
- **Inteligencia sensible** — Evaluaciones de riesgo, hipótesis, escenarios
- **Datos clasificados** — Owner (radar territorial), Médico (PHI)
- **Fuentes de inteligencia** — 30+ fuentes gubernamentales, académicas, sanitarias
- **Integridad epistemológica** — Prevención de manipulación, desinformación, poison de datos

**Amenazas consideradas:**

- 🎯 Actores estatales (CNI, CIA, SVR, Mossad, etc.)
- 🎯 Actores no estatales (hacktivistas, criminales, terroristas)
- 🎯 Amenazas internas (insider threats, compromiso de credenciales)
- 🎯 Guerra híbrida (desinformación, manipulación, influence operations)
- 🎯 Ciberataques avanzados (APT, zero-days, supply chain)

---

## 🏛️ Marco de Seguridad

### Estándares Aplicados

| Estándar | Nivel | Aplicación |
|---|---|---|
| **NIST SP 800-53** | Alto (Federal) | Controles de seguridad |
| **NIST CSF** | Tier 3 | Identify, Protect, Detect, Respond, Recover |
| **ISO 27001** | Certificado | SGSI (Sistema de Gestión de Seguridad) |
| **MITRE ATT&CK** | Enterprise | Detección de técnicas APT |
| **OWASP Top 10** | A-F | Seguridad de aplicaciones |
| **CIS Controls v8** | IG2 | Controles esenciales |
| **GDPR** | Compliance | Protección de datos (UE) |
| **HIPAA** | Compliance | Datos médicos (EEUU) |
| **ENS** | Alto | Esquema Nacional de Seguridad (España) |

---

## 🔐 Arquitectura de Seguridad

### Modelo de Confianza Cero (Zero Trust)

**Principios:**

- ✅ **Nunca confiar, siempre verificar** — Autenticación y autorización continuas
- ✅ **Mínimo privilegio** — Solo acceso necesario, solo cuando necesario
- ✅ **Microsegmentación** — Redes, servicios, datos aislados
- ✅ **Asume compromiso** — Detecta, contiene, responde

**Implementación:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PERÍMETRO EXTERNO                         │
│  -  WAF (Web Application Firewall)                            │
│  -  DDoS Protection (Cloudflare, AWS Shield)                  │
│  -  Rate Limiting Global (100 req/min por IP)                 │
│  -  Geo-blocking (países de riesgo)                           │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    PERÍMETRO INTERNO                         │
│  -  API Gateway (autenticación, autorización)                 │
│  -  Service Mesh (mTLS entre servicios)                       │
│  -  Network Segmentation (VPC, subnets, security groups)      │
│  -  IDS/IPS (Intrusion Detection/Prevention)                  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    PERÍMETRO DE DATOS                        │
│  -  Encriptación (TLS 1.3, AES-256-GCM)                       │
│  -  Tokenización (datos sensibles)                            │
│  -  Data Loss Prevention (DLP)                                │
│  -  Database Activity Monitoring (DAM)                        │
└─────────────────────────────────────────────────────────────┘
```

### Separación de Perímetros (Air Gap Lógico)

```
┌─────────────────────────────────────────────────────────────┐
│              CAPA PÚBLICA (Sin clasificar)                   │
│  -  Datos públicos, verificados                               │
│  -  Sin autenticación o mínima                                │
│  -  Rate limiting agresivo                                    │
│  -  CDN (Cloudflare)                                          │
└─────────────────────────────────────────────────────────────┘
                    ↕ [API Gateway + JWT + WAF]
┌─────────────────────────────────────────────────────────────┐
│              CAPA OWNER (Clasificado: RESTRINGIDO)           │
│  -  Radar territorial, alertas, riesgos                       │
│  -  JWT obligatorio + MFA (TOTP/WebAuthn)                     │
│  -  Network segmentation (VPC privada)                        │
│  -  Database encryption (TDE)                                 │
│  -  Auditoría completa (SIEM)                                 │
└─────────────────────────────────────────────────────────────┘
                    ↕ [Encriptación + ACLs estrictas]
┌─────────────────────────────────────────────────────────────┐
│              CAPA MÉDICA (Clasificado: CONFIDENCIAL)         │
│  -  Datos clínicos, PHI (HIPAA)                               │
│  -  Encriptación cliente (Web Crypto API)                     │
│  -  Encriptación servidor (AES-256-GCM)                       │
│  -  Acceso solo profesionales autorizados                     │
│  -  NUNCA se cruza con Owner (air gap lógico)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Controles de Seguridad (NIST 800-53)

### AC (Access Control)

| Control | Implementación | Nivel |
|---|---|---|
| **AC-2** Account Management | Usuarios creados solo por OWNER, revisión trimestral | Alto |
| **AC-3** Access Enforcement | RBAC + policy-based authorization | Alto |
| **AC-6** Least Privilege | Roles con mínimos permisos necesarios | Alto |
| **AC-7** Unsuccessful Login Attempts | 5 intentos → 15 min bloqueo | Alto |
| **AC-8** System Use Notification | Banner de advertencia en login | Medio |
| **AC-11** Session Lock | Timeout 15 min inactividad | Alto |
| **AC-17** Remote Access | VPN + MFA para acceso remoto | Alto |
| **AC-18** Wireless Access | WiFi corporativa segmentada | Medio |

### AU (Audit and Accountability)

| Control | Implementación | Nivel |
|---|---|---|
| **AU-2** Auditable Events | LOGIN, LOGOUT, CREATE, READ, UPDATE, DELETE, EXPORT, etc. | Alto |
| **AU-3** Content of Audit Records | Timestamp, usuario, acción, recurso, IP, user-agent, resultado | Alto |
| **AU-6** Audit Review, Analysis, and Reporting | SIEM (ELK Stack), alertas automáticas | Alto |
| **AU-9** Protection of Audit Information | Logs inmutables, append-only, WORM storage | Alto |
| **AU-12** Audit Generation | Logs automáticos para todos los eventos críticos | Alto |

### AT (Awareness and Training)

| Control | Implementación | Nivel |
|---|---|---|
| **AT-2** Security Awareness Training | Training obligatorio anual | Medio |
| **AT-3** Role-Based Security Training | Training específico por rol (OWNER, ANALYST, MEDICAL) | Alto |
| **AT-4** Security Training Records | Registro de training completado | Medio |

### CM (Configuration Management)

| Control | Implementación | Nivel |
|---|---|---|
| **CM-2** Baseline Configuration | Hardening guides (CIS benchmarks) | Alto |
| **CM-6** Configuration Settings | Configuration management (Ansible, Terraform) | Alto |
| **CM-7** Least Functionality | Solo servicios necesarios habilitados | Alto |
| **CM-8** Information System Component Inventory | Inventario automático de activos | Alto |
| **CM-10** Software Usage Restrictions | Solo software aprobado | Medio |

### CP (Contingency Planning)

| Control | Implementación | Nivel |
|---|---|---|
| **CP-2** Contingency Plan | Plan de continuidad de negocio (BCP) | Alto |
| **CP-6** Alternate Storage Site | Backups en región diferente (DR) | Alto |
| **CP-7** Alternate Processing Site | Failover automático (multi-AZ) | Alto |
| **CP-9** Information System Backup | Backups diarios, encriptados, testeados | Alto |
| **CP-10** Information System Recovery and Reconstitution | RTO < 4h, RPO < 1h | Alto |

### IA (Identification and Authentication)

| Control | Implementación | Nivel |
|---|---|---|
| **IA-2** Identification and Authentication (Organizational Users) | JWT + MFA (TOTP/WebAuthn) | Alto |
| **IA-5** Authenticator Management | Secrets en vault, rotación 90 días | Alto |
| **IA-6** Authenticator Feedback | Mensajes genéricos de error (no revelar si usuario existe) | Alto |
| **IA-7** Cryptographic Module Authentication | FIPS 140-2 validated modules | Alto |

### IR (Incident Response)

| Control | Implementación | Nivel |
|---|---|---|
| **IR-2** Incident Response Training | Training anual, simulacros | Alto |
| **IR-4** Incident Handling | Procedimientos documentados, automatización | Alto |
| **IR-5** Incident Monitoring | SIEM, correlación de eventos | Alto |
| **IR-6** Incident Reporting | Reporte a dirección, autoridades (GDPR 72h) | Alto |
| **IR-7** Incident Response Assistance | Equipo de respuesta (CSIRT) | Alto |
| **IR-8** Incident Response Plan | Plan documentado, actualizado anualmente | Alto |

### SC (System and Communications Protection)

| Control | Implementación | Nivel |
|---|---|---|
| **SC-7** Boundary Protection | Firewalls, WAF, IDS/IPS | Alto |
| **SC-8** Transmission Confidentiality and Integrity | TLS 1.3, HSTS | Alto |
| **SC-12** Cryptographic Key Establishment and Management | KMS/HSM, rotación 90 días | Alto |
| **SC-13** Cryptographic Protection | AES-256-GCM, RSA-4096 | Alto |
| **SC-28** Protection of Information at Rest | TDE, filesystem encriptado | Alto |

### SI (System and Information Integrity)

| Control | Implementación | Nivel |
|---|---|---|
| **SI-2** Flaw Remediation | Patch management (crítico < 24h) | Alto |
| **SI-3** Malicious Code Protection | Antivirus, EDR (Endpoint Detection and Response) | Alto |
| **SI-4** Information System Monitoring | SIEM, IDS/IPS, network monitoring | Alto |
| **SI-5** Security Alerts, Advisories, and Directives | Subscripción a CVE, CISA alerts | Alto |
| **SI-16** Memory Protection | DEP, ASLR habilitados | Alto |

---

## 🔑 Gestión de Identidades y Accesos (IAM)

### Autenticación

#### JWT (JSON Web Tokens)

**Configuración de nivel militar:**

```
Algoritmo: RS256 (asimétrico, no HS256)
Tamaño de clave: RSA-4096
Access token: 15 minutos (corto)
Refresh token: 24 horas
Issuer: ceutia.system
Audience: ceutia.clients
JTI (JWT ID): UUID único por token
```

**Claims obligatorios:**

```json
{
  "sub": "user-uuid",
  "iss": "ceutia.system",
  "aud": "ceutia.clients",
  "exp": 1694260800,
  "iat": 1694260200,
  "nbf": 1694260200,
  "jti": "token-uuid",
  "role": "OWNER",
  "permissions": ["alerts:read", "alerts:write", /* ... */],
  "mfa_verified": true,
  "device_id": "device-uuid",
  "ip_address": "192.168.1.1"
}
```

**Validaciones estrictas:**

- ✅ Verificar firma (RS256)
- ✅ Verificar expiración (exp)
- ✅ Verificar issuer (iss)
- ✅ Verificar audience (aud)
- ✅ Verificar JTI único (no replay)
- ✅ Verificar MFA (mfa_verified: true)
- ✅ Verificar IP/device (opcional, alto seguridad)

**Rotación de claves:**

- ✅ Claves RSA rotadas cada 90 días
- ✅ JWKS endpoint público (/.well-known/jwks.json)
- ✅ Key versioning (kid claim)
- ✅ Revocación inmediata en compromiso

#### MFA (Multi-Factor Authentication)

**Obligatorio para:**

- ✅ OWNER
- ✅ SENIOR_ANALYST
- ✅ MEDICAL_PROFESSIONAL
- ✅ Cualquier rol con acceso a datos clasificados

**Métodos soportados (orden de preferencia):**

1. ✅ **WebAuthn / FIDO2** (hardware keys: YubiKey, Titan) — Nivel más alto
2. ✅ **TOTP** (Google Authenticator, Authy, Microsoft Authenticator)
3. ✅ **Push notification** (Duo, Okta Verify)
4. ⚠️ **SMS** (solo fallback, no recomendado para alto riesgo)

**Requisitos:**

- ✅ MFA obligatorio en login
- ✅ MFA obligatorio para operaciones críticas (export, delete, config changes)
- ✅ Backup codes (10 códigos, generados criptográficamente, un solo uso)
- ✅ Device trust (recordar dispositivo 30 días, luego MFA de nuevo)
- ✅ Revocación inmediata de dispositivos comprometidos

#### Passwords

**Política de nivel militar:**

- ✅ Mínimo **16 caracteres** (no 12)
- ✅ Complejidad: mayúsculas, minúsculas, números, símbolos
- ✅ No diccionario (verificar contra listas de passwords comunes)
- ✅ No reutilización de últimas **24 passwords** (no 10)
- ✅ Expiración: **60 días** (no 90, más estricto)
- ✅ Bloqueo: **3 intentos fallidos** → **30 minutos** (no 5/15)
- ✅ Hashing: **Argon2id** (no bcrypt, más resistente a GPU/ASIC)
- ✅ Salt: 128 bits mínimo
- ✅ Memory cost: 64 MB, time cost: 3, parallelism: 4

**Verificación contra listas de passwords comprometidos:**

```typescript
import { PwnedPassword } from 'hibp';

async function validatePassword(password: string): Promise<boolean> {
  // Verificar contra Have I Been Pwned
  const pwned = await PwnedPassword(password);
  if (pwned) {
    throw new Error('Password appears in known breaches');
  }
  
  // Verificar complejidad
  if (password.length < 16) {
    throw new Error('Password must be at least 16 characters');
  }
  
  // Verificar no diccionario
  // ...
  
  return true;
}
```

### Autorización

#### RBAC (Role-Based Access Control)

**Matriz de acceso:**

| Recurso | OWNER | SENIOR_ANALYST | JUNIOR_ANALYST | MEDICAL | CITIZEN |
|---|---|---|---|---|---|
| **Alerts** | CRUDA | CRUD | R | R | R (públicas) |
| **Risks** | CRUDA | CRUD | R | R | - |
| **Hypotheses** | CRUDA | CRUD | R | R | - |
| **Scenarios** | CRUDA | CRUD | R | R | - |
| **Sources** | CRUDA | CRU | R | R | R |
| **Documents** | CRUDA | CRU | CR | R | R |
| **Users** | CRUDA | RU | R | R | R (propio) |
| **Roles** | CRUDA | R | - | - | - |
| **Config** | CRUDA | RU | R | R | R (pública) |
| **Audit** | RA | R | - | R | - |
| **Medical** | R | R | - | CRUDA | RW (propio) |

**Leyenda:** C=Create, R=Read, U=Update, D=Delete, A=Admin

#### ABAC (Attribute-Based Access Control)

**Para acceso granular:**

```typescript
// Policy: Solo acceso a datos del propio dominio
function domainAccessPolicy(user: User, resource: Resource): boolean {
  if (user.role === 'OWNER') return true;
  if (user.role === 'SENIOR_ANALYST') return true;
  if (user.role === 'JUNIOR_ANALYST') {
    return user.assignedDomains.includes(resource.domain);
  }
  return false;
}

// Policy: Solo acceso en horario laboral (para ciertos roles)
function timeBasedPolicy(user: User, request: Request): boolean {
  if (user.role === 'OWNER') return true;
  if (user.role === 'SENIOR_ANALYST') return true;
  
  const hour = new Date().getHours();
  return hour >= 8 && hour <= 20; // 8:00 - 20:00
}

// Policy: Solo desde IPs corporativas (para Owner)
function locationBasedPolicy(user: User, request: Request): boolean {
  if (user.role !== 'OWNER') return true;
  
  const corporateIPs = ['192.168.1.0/24', '10.0.0.0/8'];
  return isIPInRange(request.ip, corporateIPs);
}
```

#### Policy Engine

**Implementación con Open Policy Agent (OPA):**

```rego
# policy.rego
package ceutia.authz

default allow = false

# Owner tiene acceso total
allow {
  input.user.role == "OWNER"
}

# Senior analyst tiene acceso read/write a alerts
allow {
  input.user.role == "SENIOR_ANALYST"
  input.resource == "alerts"
  input.action in ["read", "write", "create", "update", "delete"]
}

# Junior analyst solo tiene acceso read a alerts
allow {
  input.user.role == "JUNIOR_ANALYST"
  input.resource == "alerts"
  input.action == "read"
}

# Medical solo tiene acceso a medical
allow {
  input.user.role == "MEDICAL_PROFESSIONAL"
  input.resource == "medical"
}

# Citizen solo tiene acceso read a public
allow {
  input.user.role == "CITIZEN"
  input.resource == "public"
  input.action == "read"
}
```

---

## 🔒 Encriptación

### En Tránsito

**Configuración TLS 1.3 (nivel militar):**

```nginx
# Nginx configuration
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers off;

# Cipher suites (solo fuertes)
ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';

# HSTS (1 año, includeSubDomains, preload)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Certificate transparency
add_header Expect-CT "max-age=31536000; enforce; report-uri=\"[https://ceutia.report-uri.com/rpt/ct](https://ceutia.report-uri.com/rpt/ct)\"" always;
```

**Certificados:**

- ✅ CA comercial (DigiCert, Sectigo) o Let's Encrypt (dev)
- ✅ Validación OV (Organization Validated) mínimo
- ✅ EV (Extended Validation) recomendado para producción
- ✅ Rotación automática (90 días Let's Encrypt, 1-2 años comercial)
- ✅ Certificate pinning (mobile apps)

### En Reposo

#### Base de Datos

**PostgreSQL TDE (Transparent Data Encryption):**

```sql
-- Habilitar encriptación
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- Encriptación a nivel de columna (datos sensibles)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE medical_consultations (
  id UUID PRIMARY KEY,
  patient_id UUID NOT NULL,
  symptoms_encrypted BYTEA NOT NULL, -- Encriptado
  diagnosis_encrypted BYTEA, -- Encriptado
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Función de encriptación
CREATE OR REPLACE FUNCTION encrypt_data(data TEXT, key TEXT)
RETURNS BYTEA AS $$
BEGIN
  RETURN pgp_sym_encrypt(data, key);
END;
$$ LANGUAGE plpgsql;

-- Función de desencriptación
CREATE OR REPLACE FUNCTION decrypt_data(data BYTEA, key TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN pgp_sym_decrypt(data, key);
END;
$$ LANGUAGE plpgsql;
```

#### Object Storage

**S3 Server-Side Encryption:**

```json
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:eu-west-1:123456789012:key/12345678-1234-1234-1234-123456789012"
      }
    }
  ]
}
```

**Encriptación cliente (antes de subir):**

```typescript
import { createCipheriv, randomBytes } from 'crypto';

function encryptFile(file: Buffer, key: Buffer): { ciphertext: Buffer, iv: Buffer } {
  const iv = randomBytes(16);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  
  let ciphertext = cipher.update(file);
  ciphertext = Buffer.concat([ciphertext, cipher.final()]);
  
  return { ciphertext, iv };
}
```

#### Backups

**Encriptación de backups:**

```bash
# Encriptar backup con GPG
gpg --symmetric --cipher-algo AES256 --output backup.sql.gpg backup.sql

# O con OpenSSL
openssl enc -aes-256-cbc -salt -in backup.sql -out backup.sql.enc -pass pass:$BACKUP_PASSWORD
```

**Almacenamiento seguro:**

- ✅ Backups encriptados (AES-256)
- ✅ Keys en KMS/HSM separado
- ✅ Regiones diferentes (DR)
- ✅ Acceso limitado (solo Owner + backup service)

---

## 🚫 Prevención de Amenazas Avanzadas

### APT (Advanced Persistent Threats)

#### Detección

**Señales de APT:**

- 🚨 Reconocimiento prolongado (scanning, enumeration)
- 🚨 Movimiento lateral (acceso a múltiples sistemas)
- 🚨 Persistencia (backdoors, scheduled tasks)
- 🚨 Exfiltración (tráfico inusual, horarios extraños)
- 🚨 Credential dumping (mimikatz, hashes)

**Controles de detección:**

- ✅ SIEM (correlación de eventos)
- ✅ EDR (Endpoint Detection and Response)
- ✅ Network Traffic Analysis (NTA)
- ✅ User Behavior Analytics (UBA)
- ✅ Honeypots (detección de intrusos)

#### Mitigación

- ✅ Patch management agresivo (crítico < 24h)
- ✅ Application whitelisting
- ✅ Network segmentation (microsegmentación)
- ✅ Least privilege estricto
- ✅ MFA universal
- ✅ Logging centralizado (SIEM)
- ✅ Incident response plan probado

### Supply Chain Attacks

#### Prevención

**Dependencias:**

- ✅ Lock files (package-lock.json, yarn.lock)
- ✅ Dependency scanning (npm audit, Snyk, Dependabot)
- ✅ Private registry (npm registry privado, Nexus, Artifactory)
- ✅ Code signing (commits firmados con GPG)
- ✅ CI/CD seguro (GitHub Actions con OIDC, no secrets hardcoded)

**Infraestructura:**

- ✅ Infrastructure as Code (Terraform, versionado)
- ✅ Immutable infrastructure (no cambios manuales)
- ✅ Golden images (pre-hardened, escaneadas)
- ✅ Container scanning (Trivy, Clair)

### Insider Threats

#### Detección

**Señales:**

- 🚨 Acceso a datos fuera de horario laboral
- 🚨 Descarga masiva de datos
- 🚨 Acceso a recursos no relacionados con el rol
- 🚨 Múltiples intentos de acceso fallidos
- 🚨 Uso de dispositivos USB no autorizados

**Controles:**

- ✅ DLP (Data Loss Prevention)
- ✅ UEBA (User and Entity Behavior Analytics)
- ✅ Logging de todas las acciones (auditoría)
- ✅ Separación de duties (no una persona controla todo)
- ✅ Background checks (para roles críticos)

---

## 🛡️ Defensas Perimetrales

### WAF (Web Application Firewall)

**Reglas OWASP CRS (Core Rule Set):**

```
# ModSecurity / OWASP CRS
SecRuleEngine On
SecRequestBodyAccess On
SecResponseBodyAccess Off

# SQL Injection
SecRule ARGS "@detectSQLi" "id:1,deny,status:403,msg:'SQL Injection'"

# XSS
SecRule ARGS "@detectXSS" "id:2,deny,status:403,msg:'XSS'"

# RCE
SecRule ARGS "@detectRCE" "id:3,deny,status:403,msg:'RCE'"

# Path Traversal
SecRule ARGS "@detectPathTraversal" "id:4,deny,status:403,msg:'Path Traversal'"
```

**Reglas personalizadas:**

```
# Bloquear países de riesgo (ejemplos)
SecRule GEO:COUNTRY_CODE "@pmFromFile geo-ip-blocklist.txt" "id:100,deny,status:403"

# Rate limiting por IP
SecAction "id:200,phase:1,nolog,pass,initcol:ip=%{REMOTE_ADDR},setvar:ip.request_count=+1,expirevar:ip.request_count=60"
SecRule IP:REQUEST_COUNT "@gt 100" "id:201,deny,status:429,msg:'Rate limit exceeded'"
```

### DDoS Protection

**Cloudflare / AWS Shield:**

- ✅ Rate limiting global (100 req/min por IP)
- ✅ Challenge (CAPTCHA) para tráfico sospechoso
- ✅ Geo-blocking (países de riesgo)
- ✅ Bot protection (detección de bots)
- ✅ Anycast (distribución de tráfico)
- ✅ Auto-scaling (absorber picos)

**Configuración:**

```json
{
  "rate_limit": {
    "threshold": 100,
    "period": 60,
    "action": "block"
  },
  "waf": {
    "rules": ["owasp-crs", "custom-rules"],
    "mode": "block"
  },
  "bot_fight_mode": "on",
  "geo_restrictions": {
    "whitelist": ["ES", "PT", "FR", "DE", "GB", "US"],
    "block_unknown": false
  }
}
```

### IDS/IPS (Intrusion Detection/Prevention)

**Snort / Suricata reglas:**

```
# Detectar scanning
alert tcp any any -> any any (msg:"Port scan detected"; flags:S; threshold:type threshold, track by_src, count 20, seconds 60; sid:1000001;)

# Detectar brute force SSH
alert tcp any any -> any 22 (msg:"SSH brute force"; flow:to_server; threshold:type threshold, track by_src, count 5, seconds 60; sid:1000002;)

# Detectar SQL injection
alert http any any -> any any (msg:"SQL injection attempt"; content:"SELECT"; nocase; content:"FROM"; nocase; sid:1000003;)
```

---

## 📊 Monitoreo y Detección (SIEM)

### SIEM (Security Information and Event Management)

**Stack:** ELK (Elasticsearch, Logstash, Kibana) + Wazuh

**Logs centralizados:**

- ✅ Application logs (todos los servicios)
- ✅ System logs (syslog, journalctl)
- ✅ Database logs (PostgreSQL audit)
- ✅ Network logs (firewall, IDS/IPS)
- ✅ Access logs (WAF, API Gateway)
- ✅ Authentication logs (JWT, MFA, login attempts)

**Correlación de eventos:**

```
# Regla de correlación: Brute force + Login exitoso = Compromiso potencial
IF
  failed_login_attempts >= 5 FROM same_ip WITHIN 5_minutes
  AND successful_login FROM same_ip WITHIN 10_minutes
THEN
  alert_severity = "HIGH"
  alert_message = "Possible compromised account after brute force"
  actions = [notify_soc, lock_account, force_password_reset]
```

### Alertas de Seguridad

**Niveles:**

| Nivel | Descripción | Ejemplo | Response Time |
|---|---|---|---|
| **Crítico** | Brecha activa, sistema comprometido | Data exfiltration, ransomware | Inmediato (< 15 min) |
| **Alto** | Ataque en progreso, vulnerabilidad explotada | SQL injection exitoso, APT detectado | < 1 hora |
| **Medio** | Intento de ataque bloqueado | Brute force detectado, scanning | < 4 horas |
| **Bajo** | Anomalía menor, configuración insegura | Tráfico inusual, certificado próximo a expirar | < 24 horas |

**Canales de notificación:**

- ✅ Crítico: PagerDuty, SMS, teléfono
- ✅ Alto: Slack, email, Telegram
- ✅ Medio: Email, Slack
- ✅ Bajo: Email, dashboard

---

## 🚨 Respuesta a Incidentes

### CSIRT (Computer Security Incident Response Team)

**Roles:**

- ✅ **Incident Manager** — Coordina respuesta
- ✅ **Technical Lead** — Análisis técnico, contención
- ✅ **Communications** — Notificaciones internas/externas
- ✅ **Legal/Compliance** — GDPR, autoridades
- ✅ **Forensics** — Preservación de evidencia

### Procedimiento de Respuesta

**Fases (NIST SP 800-61):**

1. ✅ **Preparación** — Herramientas, training, procedimientos
2. ✅ **Detección y Análisis** — Identificar, clasificar, priorizar
3. ✅ **Contención, Erradicación y Recuperación** — Aislar, eliminar, restaurar
4. ✅ **Post-Incident Activity** — Lecciones aprendidas, mejoras

### Playbooks

#### Playbook: SQL Injection

```
1. DETECCIÓN
   - WAF detecta patrón SQL injection
   - SIEM correlaciona múltiples intentos

2. CLASIFICACIÓN
   - Nivel: Alto (si exitoso), Medio (si bloqueado)

3. CONTENCIÓN
   - Bloquear IP atacante (WAF, firewall)
   - Invalidar sesiones desde esa IP
   - Si exitoso: revocar accesos comprometidos

4. ANÁLISIS
   - Revisar logs (WAF, application, database)
   - Determinar alcance (qué datos accedidos)
   - Identificar vulnerabilidad (endpoint, query)

5. ERRADICACIÓN
   - Patchear vulnerabilidad (input validation, parameterized queries)
   - Rotar credentials si comprometidos

6. RECUPERACIÓN
   - Restaurar servicio normal
   - Monitorear actividad sospechosa

7. POST-INCIDENT
   - Documentar incidente
   - Lecciones aprendidas
   - Mejorar controles (WAF rules, code review)
```

#### Playbook: Data Exfiltration

```
1. DETECCIÓN
   - DLP detecta transferencia masiva de datos
   - SIEM correlaciona con acceso inusual

2. CLASIFICACIÓN
   - Nivel: Crítico

3. CONTENCIÓN
   - Bloquear transferencia (firewall, DLP)
   - Revocar accesos del usuario/IP
   - Aislar sistema comprometido

4. ANÁLISIS
   - Determinar qué datos exfiltrados
   - Identificar vector de ataque
   - Determinar alcance temporal

5. NOTIFICACIÓN
   - Dirección (inmediato)
   - Autoridades (GDPR 72h)
   - Usuarios afectados (si PHI o datos personales)

6. ERRADICACIÓN Y RECUPERACIÓN
   - Eliminar acceso atacante
   - Patchear vulnerabilidades
   - Rotar todos los secrets

7. POST-INCIDENT
   - Forensics completo
   - Mejoras de controles
   - Training adicional
```

---

## 📝 Cumplimiento y Auditoría

### Auditorías

**Internas:**

- ✅ Mensual: revisión de accesos, permisos, logs
- ✅ Trimestral: vulnerability scanning, penetration testing
- ✅ Semestral: auditoría completa de seguridad
- ✅ Anual: certificación (ISO 27001, SOC 2)

**Externas:**

- ✅ Anual: auditoría ISO 27001
- ✅ Anual: SOC 2 Type II
- ✅ Bienal: penetration testing por terceros
- ✅ Continuo: vulnerability scanning (external)

### Certificaciones

| Certificación | Nivel | Estado |
|---|---|---|
| **ISO 27001** | Certificado | Requerido (producción) |
| **SOC 2 Type II** | Certificado | Requerido (producción) |
| **ENS Alto** | Certificado | Requerido (España, sector público) |
| **HIPAA** | Compliance | Requerido (módulo médico) |
| **GDPR** | Compliance | Requerido (UE) |

### Reportes de Vulnerabilidades

**Proceso seguro:**

1. ✅ Reporte recibido (security@ceutia.system, PGP encriptado)
2. ✅ Acknowledgment (24 horas)
3. ✅ Triaje (clasificar severidad: crítico, alto, medio, bajo)
4. ✅ Reproducción (validar vulnerabilidad)
5. ✅ Fix (desarrollar, testear, code review)
6. ✅ Despliegue (patch en producción)
7. ✅ Notificación (reporter, usuarios si afectado, autoridades si requerido)
8. ✅ Publicación (security advisory, CVE si aplica)
9. ✅ Post-mortem (lecciones aprendidas)

**Tiempos de respuesta (SLA):**

| Severidad | Acknowledgment | Fix | Publicación |
|---|---|---|---|
| **Crítico** | 4 horas | 24 horas | 72 horas |
| **Alto** | 24 horas | 7 días | 14 días |
| **Medio** | 72 horas | 30 días | 60 días |
| **Bajo** | 7 días | 90 días | 180 días |

**Recompensas (Bug Bounty):**

- ✅ Crítico: €5,000 - €10,000
- ✅ Alto: €2,000 - €5,000
- ✅ Medio: €500 - €2,000
- ✅ Bajo: €100 - €500

---

## 🎯 Métricas de Seguridad (KPIs)

| Métrica | Objetivo | Frecuencia |
|---|---|---|
| **Time to Detect (MTTD)** | < 1 hora | Mensual |
| **Time to Respond (MTTR)** | < 4 horas | Mensual |
| **Vulnerability Patch Time (crítico)** | < 24 horas | Semanal |
| **Failed Login Rate** | < 1% | Diario |
| **MFA Adoption** | 100% (roles privilegiados) | Mensual |
| **Security Training Completion** | 100% | Trimestral |
| **Incident Count** | Tendencia decreciente | Mensual |
| **Audit Findings Remediation** | 100% en 30 días | Mensual |

---

## 📞 Contacto

**Reportar vulnerabilidades:**

- Email: security@ceutia.system (PGP: [fingerprint])
- GitHub: Security Advisories (privado)
- Signal: +XX XXX XXX XXX (solo emergencias críticas)

**NUNCA reportar en:**

- ❌ Issues públicos de GitHub
- ❌ Foros públicos
- ❌ Redes sociales
- ❌ Email no encriptado (si contiene detalles sensibles)

**Emergencias críticas (brecha activa):**

- Teléfono: +XX XXX XXX XXX (24/7)
- Signal: +XX XXX XXX XXX
- Telegram: @ceutia_security

---

*Esta política de seguridad es **vinculante** para todos los componentes, contribuidores y operadores de CEUTIA.*

*Su cumplimiento es **obligatorio** para proteger infraestructura crítica de inteligencia territorial.*

*Violaciones serán investigadas y pueden resultar en acciones disciplinarias, legales o penales.*

---

**Clasificación:** RESTRINGIDO  
**Última actualización:** Septiembre 2026  
**Versión:** 2.0.0  
**Próxima revisión:** Diciembre 2026
```

***