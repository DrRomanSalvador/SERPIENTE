SECURITY_ARCHITECTURE.md

# Arquitectura de Seguridad de CEUTIA
## 1. Propósito
Este documento define la arquitectura de seguridad de CEUTIA como un sistema de protección integral de:
- identidad;
- acceso;
- infraestructura;
- aplicaciones;
- datos;
- fuentes;
- evidencia;
- conocimiento;
- modelos;
- configuración;
- trazabilidad;
- integridad epistemológica.
La seguridad de CEUTIA no se limita a impedir accesos no autorizados.
Debe impedir también que información manipulada, evidencia contaminada, relaciones falsas, modelos comprometidos o configuraciones alteradas produzcan conclusiones analíticas que aparenten ser fiables.
---
## 2. Principio Fundamental
CEUTIA debe proteger simultáneamente dos superficies de seguridad:
```text
SUPERFICIE TÉCNICA
        │
        ├── identidad
        ├── autenticación
        ├── autorización
        ├── red
        ├── infraestructura
        ├── aplicaciones
        ├── secretos
        └── datos
SUPERFICIE EPISTÉMICA
        │
        ├── fuentes
        ├── procedencia
        ├── evidencia
        ├── corroboración
        ├── independencia
        ├── contradicción
        ├── incertidumbre
        ├── hipótesis
        ├── modelos
        └── conclusiones

Ambas superficies deben estar conectadas mediante controles verificables.

⸻

3. Modelo de Amenaza

CEUTIA debe asumir que un atacante puede intentar:

1. acceder sin autorización;
2. robar credenciales;
3. modificar datos;
4. introducir información falsa;
5. manipular fuentes;
6. contaminar evidencia;
7. alterar metadatos de procedencia;
8. provocar falsos positivos;
9. provocar falsos negativos;
10. manipular modelos;
11. modificar configuraciones;
12. ocultar actividad;
13. exfiltrar información;
14. degradar la disponibilidad;
15. explotar dependencias;
16. comprometer la cadena de suministro;
17. utilizar cuentas legítimas;
18. explotar errores humanos;
19. inducir decisiones mediante información manipulada.

La arquitectura debe considerar tanto ataques directos como ataques indirectos.

⸻

4. Modelo de Confianza

CEUTIA adopta un modelo de confianza mínima.

NINGÚN COMPONENTE
    ↓
SE CONSIDERA CONFIABLE
    ↓
POR SU SIMPLE UBICACIÓN

La confianza debe derivarse de:

* identidad;
* autenticación;
* autorización;
* contexto;
* integridad;
* procedencia;
* estado del dispositivo o servicio cuando sea aplicable;
* clasificación del recurso;
* política vigente.

⸻

5. Defensa en Profundidad

Ningún control individual debe considerarse suficiente.

La arquitectura utiliza capas:

Internet
   ↓
DNS / TLS
   ↓
Edge / Reverse Proxy
   ↓
WAF
   ↓
Rate Limiting
   ↓
API
   ↓
Authentication
   ↓
Authorization
   ↓
Application
   ↓
Data Access Policy
   ↓
Database
   ↓
Audit

Para información analítica:

Source
   ↓
Ingestion
   ↓
Integrity
   ↓
Provenance
   ↓
Evidence
   ↓
Epistemic Validation
   ↓
Claim
   ↓
Model
   ↓
Output

⸻

6. Identidad

Toda identidad debe ser explícita.

El sistema debe distinguir como mínimo:

human user
service account
machine identity
ingestion connector
model identity
scheduled job
administrative identity

Las identidades de máquinas no deben compartir credenciales con usuarios humanos.

⸻

7. Autenticación

La autenticación debe:

* utilizar mecanismos criptográficamente seguros;
* evitar contraseñas almacenadas en texto plano;
* utilizar hashing resistente a ataques offline;
* soportar MFA;
* permitir rotación de credenciales;
* limitar intentos;
* registrar eventos relevantes;
* invalidar sesiones comprometidas.

Las cuentas privilegiadas deben estar sometidas a controles adicionales.

⸻

8. Autorización

CEUTIA utiliza:

DEFAULT DENY

como principio de autorización.

Una solicitud debe satisfacer simultáneamente:

IDENTIDAD
+
AUTENTICACIÓN
+
PERMISO
+
RECURSO
+
ACCIÓN
+
CONTEXTO

antes de ser autorizada cuando el recurso lo requiera.

La ocultación de elementos en una interfaz no constituye autorización.

⸻

9. Separación PUBLIC / OWNER

La separación entre información pública y restringida debe implementarse en el servidor.

                    CEUTIA
                      │
          ┌───────────┴───────────┐
          │                       │
       PUBLIC                   OWNER
          │                       │
   Public Dataset         Restricted Dataset
          │                       │
   Public API             Owner API
          │                       │
   Public UI              Owner UI

Reglas fundamentales:

PUBLIC → OWNER = DENEGADO
PUBLIC → RESTRICTED = DENEGADO
PUBLIC → PRIVATE = DENEGADO
OWNER → PUBLIC = PERMITIDO SEGÚN POLÍTICA
OWNER → OWNER = SEGÚN AUTORIZACIÓN

La separación lógica no debe describirse como “air gap” salvo que exista una separación física real.

⸻

10. Clasificación de Datos

Todo recurso sensible debe tener una clasificación.

Clasificaciones iniciales:

PUBLIC
INTERNAL
RESTRICTED
CONFIDENTIAL
SENSITIVE
MEDICAL

La clasificación debe acompañar al recurso durante su ciclo de vida.

Una operación que reduzca la clasificación requiere autorización explícita y trazabilidad.

⸻

11. Flujo de Datos Sensibles

El acceso a información sensible debe seguir:

REQUEST
   ↓
IDENTITY
   ↓
AUTHENTICATION
   ↓
AUTHORIZATION
   ↓
CLASSIFICATION CHECK
   ↓
PURPOSE / POLICY CHECK
   ↓
DATA ACCESS
   ↓
AUDIT EVENT

Nunca:

REQUEST
   ↓
DATABASE

⸻

12. Cifrado

Los datos deben protegerse mediante cifrado en tránsito y, cuando corresponda, en reposo.

En tránsito:

TLS

En reposo:

disk/database encryption
+
encrypted backups
+
encrypted object storage

La elección concreta de algoritmos y parámetros se especificará en:

CRYPTOGRAPHY.md

No se debe confundir cifrado de determinados campos mediante funciones criptográficas con cifrado completo del almacenamiento.

⸻

13. Gestión de Claves

Las claves criptográficas deben mantenerse separadas de los datos que protegen cuando el modelo de amenaza lo requiera.

Producción debe utilizar, según la infraestructura disponible:

KMS
HSM
Vault
Cloud Secret Manager

Las claves deben tener:

identifier
owner
purpose
algorithm
creation_time
activation_time
rotation_policy
status

Estados posibles:

PENDING
ACTIVE
SUSPENDED
ROTATING
REVOKED
DESTROYED

⸻

14. Secretos

Nunca deben almacenarse en Git:

passwords
API keys
JWT private keys
TLS private keys
database credentials
cloud credentials
webhook secrets
encryption keys
tokens

Los secretos deben introducirse mediante variables de entorno seguras o sistemas dedicados de gestión de secretos.

.env.example contiene solamente referencias y valores no sensibles.

⸻

15. Seguridad de la Cadena de Datos

La cadena de información debe mantener integridad desde la adquisición hasta el resultado analítico.

SOURCE
  ↓
RAW INPUT
  ↓
OBSERVATION
  ↓
NORMALIZATION
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
ANALYSIS
  ↓
MODEL
  ↓
OUTPUT

Cada transformación material debe ser trazable.

⸻

16. Integridad de Procedencia

La procedencia debe registrar, cuando esté disponible:

source_id
source_type
origin
acquisition_method
acquired_at
published_at
observed_at
content_hash
parent_record
transformation
processor
processor_version

El objetivo es poder determinar si un resultado deriva realmente de la evidencia declarada.

⸻

17. Integridad Epistemológica

La seguridad de CEUTIA debe detectar situaciones como:

fuente comprometida
      ↓
información falsa
      ↓
evidencia contaminada
      ↓
claim incorrecto
      ↓
modelo actualizado
      ↓
predicción incorrecta
      ↓
alerta

La arquitectura debe permitir identificar y propagar el estado de compromiso hacia los objetos derivados.

Una evidencia posteriormente invalidada no debe desaparecer.

Debe conservarse su historial y marcarse su estado.

⸻

18. Corrupción de Conocimiento

Si una fuente o evidencia se determina posteriormente como comprometida, CEUTIA debe poder localizar:

evidence affected
claims affected
hypotheses affected
models affected
alerts affected
decisions or assessments affected

Esto constituye una capacidad crítica de análisis retrospectivo.

⸻

19. Contradicciones

Las contradicciones deben mantenerse separadas de los errores técnicos.

ERROR TÉCNICO
≠
CONTRADICCIÓN EVIDENCIARIA

Una contradicción puede representar información válida y mutuamente incompatible.

Debe conservarse:

claim_A
claim_B
evidence_A
evidence_B
source_A
source_B
independence
temporal_context
resolution_status

⸻

20. Independencia de Fuentes

La corroboración debe considerar dependencia entre fuentes.

Ejemplo:

SOURCE A
   ↓
ORIGINAL REPORT
   ↓
SOURCE B
   ↓
SOURCE C

A, B y C no constituyen necesariamente tres observaciones independientes.

CEUTIA debe poder representar:

source lineage
shared origin
shared evidence
syndication
citation dependency
ownership relationship

⸻

21. Seguridad de Modelos

Los modelos deben considerarse activos sensibles cuando puedan modificar resultados analíticos.

Cada modelo debe estar identificado mediante:

model_id
version
artifact_hash
training_data_reference
code_version
configuration_version
deployment_status
approval_status

Un artefacto de modelo cuya integridad no pueda verificarse no debe ejecutarse en producción.

⸻

22. Ataques contra Modelos

La arquitectura debe contemplar, cuando corresponda:

data poisoning
model poisoning
adversarial inputs
prompt injection
model extraction
model inversion
membership inference
supply-chain compromise
unsafe model updates

Los controles concretos se desarrollarán en:

AI_SECURITY.md
MODEL_SECURITY.md

⸻

23. Seguridad de Ingestores

Cada conector externo debe considerarse un componente no confiable por defecto.

Debe estar sujeto a:

authentication
authorization
timeout
rate limiting
validation
content-type validation
size limits
error handling
provenance recording
logging

La información obtenida de una fuente no debe convertirse automáticamente en conocimiento confiable.

⸻

24. Contenido Externo

Contenido procedente de Internet debe considerarse potencialmente hostil.

Puede contener:

malicious payloads
prompt injection
malformed documents
embedded scripts
tracking mechanisms
false information
misleading metadata
oversized content
unexpected encodings

Los datos externos deben permanecer separados de instrucciones internas del sistema.

⸻

25. Prompt Injection

Cuando CEUTIA procese contenido que posteriormente pueda ser enviado a un modelo de lenguaje, el contenido externo debe tratarse como:

DATA

y nunca como:

SYSTEM INSTRUCTION

Un documento externo no puede modificar por sí mismo:

system policy
authorization
security configuration
tool permissions
data-access permissions
model policy

⸻

26. APIs

Las APIs deben aplicar:

authentication
authorization
schema validation
rate limiting
input validation
output filtering
request correlation
audit logging
error sanitization

Los errores externos no deben revelar:

stack traces
credentials
internal paths
database queries
secrets
private configuration

⸻

27. Seguridad de Base de Datos

La aplicación debe utilizar:

* consultas parametrizadas;
* ORM o mecanismos equivalentes seguros;
* cuentas con privilegios mínimos;
* separación de usuarios de aplicación y administración;
* conexiones cifradas cuando corresponda;
* restricciones de integridad;
* backups protegidos;
* auditoría de operaciones sensibles.

La aplicación no debe conectarse como superusuario de PostgreSQL.

⸻

28. Seguridad de Infraestructura

Los servicios deben ejecutarse con privilegios mínimos.

Debe evitarse:

root containers
shared credentials
unnecessary exposed ports
unused services
default passwords
unrestricted management interfaces

La infraestructura debe reducir la superficie de ataque al mínimo necesario.

⸻

29. Seguridad de Contenedores

Las imágenes deben:

usar bases mínimas;
fijar versiones;
ser escaneadas;
evitar secretos;
evitar procesos privilegiados;
reducir capabilities;
utilizar usuarios no root cuando sea viable;
ser reconstruibles;
ser trazables a su origen.

⸻

30. Dependencias

Las dependencias externas constituyen parte de la superficie de ataque.

CEUTIA debe incorporar progresivamente:

dependency pinning
lockfile
vulnerability scanning
SAST
secret scanning
container scanning
SBOM
artifact provenance
release verification

Una dependencia comprometida puede comprometer toda la cadena analítica.

⸻

31. Registro de Auditoría

Los eventos relevantes deben generar registros de auditoría.

Como mínimo:

authentication
logout
authorization failure
privileged action
data access
data modification
configuration change
security event
model deployment
model execution
source modification
claim modification
hypothesis modification
alert generation
administrative action

Los registros deben protegerse frente a modificación no autorizada.

⸻

32. Integridad de Logs

Un atacante que pueda modificar sus propios logs puede destruir la capacidad de investigación.

Por ello:

APPLICATION
    ↓
AUDIT EVENT
    ↓
CENTRALIZED LOGGING
    ↓
IMMUTABILITY / ACCESS CONTROL
    ↓
MONITORING

Los logs no deben contener secretos ni datos personales innecesarios.

⸻

33. Detección

CEUTIA debe ser capaz de detectar anomalías tanto técnicas como analíticas.

Técnicas:

login anomalies
credential abuse
privilege escalation
unexpected traffic
API abuse
configuration changes
dependency anomalies

Analíticas:

unexpected source behaviour
sudden provenance changes
evidence bursts
coordinated submissions
abnormal corroboration patterns
unexpected model outputs
distribution shifts

Una anomalía no equivale automáticamente a un ataque.

Debe permanecer diferenciada de una hipótesis de compromiso.

⸻

34. Respuesta a Incidentes

Los incidentes deben seguir un ciclo:

DETECT
  ↓
TRIAGE
  ↓
CONTAIN
  ↓
ERADICATE
  ↓
RECOVER
  ↓
VERIFY
  ↓
LEARN

Los incidentes que puedan afectar la integridad epistemológica deben incluir análisis de impacto sobre:

sources
evidence
claims
hypotheses
models
alerts
historical outputs

⸻

35. Compromiso Epistémico

CEUTIA debe poder distinguir entre:

SYSTEM COMPROMISE

y:

EPISTEMIC COMPROMISE

Un sistema puede continuar funcionando técnicamente mientras sus conclusiones dejan de ser fiables.

Ejemplo:

API HEALTH = 100%
DATABASE HEALTH = 100%
MODEL HEALTH = 100%
BUT
SOURCE INTEGRITY = COMPROMISED

En este caso el sistema está operacionalmente disponible pero analíticamente comprometido.

⸻

36. Propagación de Compromiso

Cuando un objeto sea marcado como potencialmente comprometido, el sistema debe poder calcular su superficie de dependencia.

COMPROMISED SOURCE
       ↓
AFFECTED OBSERVATIONS
       ↓
AFFECTED EVIDENCE
       ↓
AFFECTED CLAIMS
       ↓
AFFECTED HYPOTHESES
       ↓
AFFECTED MODELS
       ↓
AFFECTED ALERTS

Esta capacidad debe ser implementada mediante relaciones de procedencia.

⸻

37. Estado de Confianza

Los recursos críticos pueden utilizar estados como:

UNKNOWN
UNVERIFIED
VERIFIED
CORROBORATED
CONTRADICTED
SUSPECTED
COMPROMISED
REVOKED
SUPERSEDED

Estos estados no deben confundirse con una probabilidad numérica.

⸻

38. Fail Closed

Para controles de autorización y seguridad crítica:

ERROR
↓
DENY

preferentemente frente a:

ERROR
↓
ALLOW

Una caída de un componente de autorización no debe convertirse automáticamente en acceso autorizado.

⸻

39. Resiliencia

La disponibilidad debe diseñarse mediante:

health checks
timeouts
retries controlados
circuit breakers
queue isolation
backups
restore procedures
graceful degradation
monitoring

Los reintentos deben ser limitados para evitar tormentas de tráfico.

⸻

40. Recuperación

La recuperación debe permitir:

restore
verify
reconcile
audit
resume

No debe considerarse suficiente restaurar los datos.

Debe verificarse también:

schema integrity
configuration integrity
model integrity
audit integrity
provenance integrity

⸻

41. Principio de No Ocultación

CEUTIA no debe eliminar silenciosamente:

contradictory evidence
failed predictions
false alerts
invalidated claims
compromised sources
model failures
analytical errors

Debe conservar su historial conforme a las políticas legales y de retención.

La corrección debe ser trazable.

⸻

42. Gestión de Cambios

Los cambios en componentes críticos deben quedar asociados a:

change_id
author
timestamp
reason
previous_version
new_version
review
test_result
deployment
rollback_information

Los cambios de seguridad crítica deben requerir revisión apropiada.

⸻

43. Principio de Mínimo Privilegio

Cada usuario, servicio y proceso debe recibir únicamente los permisos necesarios para realizar su función.

Debe evitarse:

global administrator
shared accounts
shared service credentials
unrestricted database access
unrestricted filesystem access

cuando una separación más precisa sea técnicamente viable.

⸻

44. Separación de Funciones

Las funciones críticas deberían separarse cuando el riesgo lo justifique.

Ejemplos:

developer
operator
security administrator
data administrator
model administrator
analyst
auditor
owner

Ninguna identidad debe acumular privilegios innecesarios.

⸻

45. Seguridad del Desarrollo

Todo cambio significativo debe pasar progresivamente por:

CODE
 ↓
STATIC ANALYSIS
 ↓
UNIT TESTS
 ↓
SECURITY TESTS
 ↓
INTEGRATION TESTS
 ↓
BUILD
 ↓
ARTIFACT VERIFICATION
 ↓
DEPLOYMENT

Los controles automatizables deben integrarse en CI/CD.

⸻

46. Seguridad de Producción

La configuración de producción debe:

desactivar debug;
desactivar credenciales de prueba;
desactivar configuraciones inseguras;
exigir TLS;
exigir autenticación;
exigir autorización;
proteger secretos;
activar auditoría;
activar monitorización;
validar configuración;

El sistema debe impedir, cuando sea posible, el arranque con configuraciones críticas incompatibles con producción.

⸻

47. Clasificación de Controles

Cada control de seguridad debe tener un estado verificable:

PLANNED
DESIGNED
IMPLEMENTED
TESTED
VERIFIED
OPERATIONAL
DEPRECATED

No debe utilizarse lenguaje de certificación para controles que no hayan sido formalmente certificados.

No debe declararse:

ISO 27001 CERTIFIED
ENS CERTIFIED
NIST CERTIFIED

sin evidencia documental válida de la certificación correspondiente.

⸻

48. Marcos de Referencia

CEUTIA puede utilizar como referencias de diseño, según aplicabilidad:

NIST Cybersecurity Framework
NIST SP 800-53
OWASP
CIS Controls
MITRE ATT&CK
ISO/IEC 27001
ENS
RGPD / GDPR

Estos marcos deben utilizarse como referencias y controles de diseño.

La existencia de una referencia en este documento no implica certificación ni conformidad automática.

⸻

49. Seguridad como Propiedad del Sistema

La seguridad de CEUTIA debe evaluarse como una propiedad emergente de la arquitectura completa.

IDENTITY
+
ACCESS
+
NETWORK
+
APPLICATION
+
DATA
+
PROVENANCE
+
MODELS
+
AUDIT
+
GOVERNANCE

Un único componente seguro no garantiza un sistema seguro.

⸻

50. Invariantes de Seguridad

Las siguientes propiedades deben considerarse invariantes arquitectónicas:

1. PUBLIC no puede acceder a OWNER sin autorización explícita.
2. OWNER no puede acceder a recursos restringidos sin autorización.
3. Toda acción privilegiada debe ser auditable.
4. Los secretos no deben almacenarse en el repositorio.
5. Los secretos no deben aparecer en logs.
6. La autorización debe ser server-side.
7. El acceso debe aplicar default-deny.
8. Los datos externos deben tratarse como no confiables.
9. La procedencia no debe perderse durante transformaciones críticas.
10. Las contradicciones no deben eliminarse silenciosamente.
11. Los modelos deben ser versionables.
12. Los outputs críticos deben poder rastrearse hasta sus inputs.
13. Un modelo no registrado no debe ejecutarse en producción.
14. Una configuración crítica no verificada no debe considerarse segura.
15. Un incidente epistemológico debe poder propagarse hacia los objetos derivados.
16. La incertidumbre material debe conservarse.
17. Las correcciones deben ser auditables.
18. Las capacidades planificadas no deben presentarse como operativas.

⸻

51. Objetivo de Seguridad

El objetivo final no es construir un sistema que simplemente resista accesos no autorizados.

El objetivo es preservar la integridad de toda la cadena:

REALIDAD
   ↓
OBSERVACIÓN
   ↓
DATOS
   ↓
EVIDENCIA
   ↓
CONOCIMIENTO
   ↓
HIPÓTESIS
   ↓
MODELO
   ↓
PREDICCIÓN
   ↓
ALERTA
   ↓
EVALUACIÓN HUMANA

La seguridad de CEUTIA debe garantizar, en la medida técnica y operacionalmente posible, que ninguna alteración no autorizada pueda atravesar esta cadena sin ser detectable, trazable o susceptible de evaluación.

⸻

52. Regla Arquitectónica Final

La confidencialidad protege la información.

La integridad protege los datos.

La autenticidad protege su origen.

La procedencia protege su historia.

La epistemología protege su significado.

La auditoría protege la capacidad de reconstruir lo ocurrido.

La gobernanza protege el uso de todo lo anterior.

CEUTIA debe proteger las siete capas.