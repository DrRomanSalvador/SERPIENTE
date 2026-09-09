
# CEUTIA — Modelo Epistemológico

> **Fundamentos epistemológicos del sistema CEUTIA**
>
> *Cómo CEUTIA comprende, evalúa y representa el conocimiento sobre fenómenos territoriales complejos*

---

## 🎯 Propósito

Este documento describe el **modelo epistemológico** que gobierna cómo CEUTIA:

- **Adquiere conocimiento** — De fuentes a observaciones
- **Evalúa conocimiento** — Calidad, independencia, corroboración
- **Representa conocimiento** — Estados epistemológicos, confianza, incertidumbre
- **Actualiza conocimiento** — Nueva evidencia, revisión de hipótesis
- **Genera conocimiento** — Hipótesis competidoras, escenarios, predicciones

**Objetivo final:** Distinguir rigurosamente entre **hecho documentado**, **declaración**, **evidencia**, **inferencia**, **hipótesis** e **incertidumbre**.

---

## 🧠 Fundamentos Filosóficos

### 1. Falibilismo (Peirce, Popper)

> **Todo conocimiento es provisional y susceptible de revisión.**

**Implicaciones para CEUTIA:**

- ✅ Ninguna afirmación es "verdad absoluta"
- ✅ Toda afirmación tiene **grado de confianza** (0-1)
- ✅ Nueva evidencia puede **revisar** confianza
- ✅ Hipótesis nunca se "prueban", solo se **corroboran provisionalmente**

**Ejemplo:**

```
Afirmación: "La tasa de desempleo en Ceuta es 25%"
- Confianza inicial: 0.95 (fuente: INE, oficial)
- Nueva evidencia contradictoria: Eurostat reporta 23%
- Confianza revisada: 0.85 (discrepancia entre fuentes)
- Incertidumbre explícita: "Entre 23-25% según fuentes"
```

---

### 2. Bayesianismo (Bayes, Jaynes)

> **La probabilidad es grado de confianza racional, actualizado con evidencia.**

**Fórmula de Bayes:**

\[
P(H|E) = \frac{P(E|H) \cdot P(H)}{P(E)}
\]

Donde:
- \( P(H|E) \) = Probabilidad de hipótesis H dada evidencia E (posterior)
- \( P(E|H) \) = Probabilidad de evidencia E si hipótesis H es cierta (likelihood)
- \( P(H) \) = Probabilidad de hipótesis H antes de ver evidencia (prior)
- \( P(E) \) = Probabilidad de evidencia E (marginal)

**Aplicación en CEUTIA:**

```
Hipótesis: "Hay aumento de polarización en Ceuta"

Prior: P(H) = 0.5 (incertidumbre inicial)

Evidencia 1: Encuesta muestra hostilidad intergrupal ↑ 30%
- P(E1|H) = 0.8 (si hay polarización, es probable ver esto)
- P(E1) = 0.4 (probabilidad marginal)
- Posterior: P(H|E1) = (0.8 × 0.5) / 0.4 = 1.0 → 0.67

Evidencia 2: Análisis de redes sociales muestra segregación discursiva ↑ 40%
- P(E2|H) = 0.7
- P(E2) = 0.3
- Posterior: P(H|E2) = (0.7 × 0.67) / 0.3 = 0.85

Evidencia 3 (contradictoria): Estudio académico no encuentra polarización significativa
- P(E3|H) = 0.2 (si hay polarización, es improbable no verla)
- P(E3) = 0.5
- Posterior: P(H|E3) = (0.2 × 0.85) / 0.5 = 0.34 → 0.60

Confianza final en hipótesis: 0.60 (incertidumbre: 0.40)
```

---

### 3. Critical Rationalism (Popper)

> **El conocimiento avanza por conjeturas y refutaciones, no por verificación.**

**Implicaciones para CEUTIA:**

- ✅ Buscar activamente **evidencia contraria** (no solo confirmatoria)
- ✅ Hipótesis rivales compiten por **mejor explicación**
- ✅ Hipótesis no se "verifican", solo **resisten intentos de refutación**
- ✅ Preferir hipótesis **más falsables** (más arriesgadas, más informativas)

**Ejemplo:**

```
Hipótesis A: "La polarización aumenta por crisis económica"
- Falsable: Si economía mejora y polarización continúa → refutada
- Riesgo: Alta (predicción específica)

Hipótesis B: "La polarización aumenta por múltiples factores"
- Falsable: Difícil (cualquier resultado es compatible)
- Riesgo: Baja (poco informativa)

Preferencia: Hipótesis A (más falsable, más informativa si resiste)
```

---

### 4. Inference to the Best Explanation (Lipton)

> **Seleccionar hipótesis que mejor explica la evidencia disponible.**

**Criterios de "mejor explicación":**

1. ✅ **Poder explicativo** — ¿Cuánta evidencia explica?
2. ✅ **Consistencia** — ¿Es internamente consistente?
3. ✅ **Coherencia** — ¿Es coherente con conocimiento establecido?
4. ✅ **Simplicidad** — ¿Es parsimoniosa (no multiplica entidades sin necesidad)?
5. ✅ **Falsabilidad** — ¿Es testable, arriesgada?

**Ejemplo:**

```
Fenómeno: Aumento de incidentes violentos en Ceuta

Hipótesis A: "Aumento por crisis económica"
- Explica: 40% de incidentes (relacionados con desempleo)
- Consistente: Sí
- Coherente: Sí (literatura sobre economía y violencia)
- Simple: Sí (un factor)
- Falsable: Sí

Hipótesis B: "Aumento por polarización sociológica + desinformación + factores económicos"
- Explica: 80% de incidentes (múltiples patrones)
- Consistente: Sí
- Coherente: Sí (literatura sobre polarización y violencia)
- Simple: No (múltiples factores)
- Falsable: Sí (pero más compleja)

Evaluación: Hipótesis B explica más evidencia, a pesar de ser menos simple.
Preferencia: Hipótesis B (mejor poder explicativo)
```

---

## 🔗 Cadena de Conocimiento

### Los 14 Eslabones

```
OBSERVACIÓN → FUENTE → PROCEDENCIA → INDEPENDENCIA → 
EVIDENCIA → CORROBORACIÓN → CONTRADICCIÓN → HIPÓTESIS → 
ALTERNATIVAS → INDICADORES → EVOLUCIÓN → PROBABILIDAD → 
CONFIANZA → IMPACTO → RIESGO → ESCENARIO → ALERTA
```

---

### 1. Observación

**Definición:** Dato bruto extraído de documento/fuente.

**Ejemplo:**

```
Texto: "La tasa de desempleo en Ceuta aumentó del 23% al 25% en el último trimestre"
- Tipo: STATE (estado)
- Dominio: ECONOMIC_SOCIAL
- Entidades: {desempleo: 25%, ubicación: Ceuta, periodo: Q3 2026}
- Fuente: INE (Instituto Nacional de Estadística)
- Fecha: 2026-09-01
```

**Calidad de observación:**

- ✅ **Extracción** — AI, regex, manual (confianza varía)
- ✅ **Contexto** — Completa, parcial, fuera de contexto
- ✅ **Ambigüedad** — Clara, ambigua, equívoca

---

### 2. Fuente

**Definición:** Origen de la observación.

**Clasificación:**

| Tipo | Ejemplos | Calidad típica |
|---|---|---|
| **GOVERNMENT_OFFICIAL** | Gobierno de España, Junta de Andalucía | VERIFIED_HIGH |
| **INTERNATIONAL_ORG** | ONU, UE, OMS | VERIFIED_HIGH |
| **ACADEMIC_RESEARCH** | Universidad de Cádiz, CSIC | VERIFIED_HIGH |
| **NEWS_MEDIA** | El País, El Mundo | VERIFIED_MEDIUM |
| **SOCIAL_MEDIA** | Twitter, Facebook | UNVERIFIED |
| **HEALTH_SYSTEM** | Ministerio de Sanidad, Hospital de Ceuta | VERIFIED_HIGH |
| **ENVIRONMENTAL_MONITOR** | AEMET, MITECO | VERIFIED_HIGH |

**Evaluación de fuente:**

- ✅ **Calidad** — VERIFIED_HIGH, VERIFIED_MEDIUM, UNVERIFIED, DISCREDITED
- ✅ **Independencia** — PRIMARY, SECONDARY_INDEPENDENT, SECONDARY_DEPENDENT
- ✅ **Historial** — ¿Ha sido confiable en el pasado?
- ✅ **Conflicto de interés** — ¿Tiene agenda, sesgo?

---

### 3. Procedencia

**Definición:** Trazabilidad completa de la observación.

**Cadena de procedencia:**

```
Documento (INE, 2026-09-01)
  ↓
Observación extraída (AI, confianza 0.95)
  ↓
Evidencia (calidad 0.9, independencia PRIMARY)
  ↓
Afirmación ("Desempleo 25%", confianza 0.9)
  ↓
Hipótesis ("Crisis económica", probabilidad 0.6)
```

**Metadatos de procedencia:**

- ✅ **Documento** — ID, título, tipo, fecha
- ✅ **Fuente** — Nombre, tipo, calidad, independencia
- ✅ **Extracción** — Método (AI, manual), confianza, fecha
- ✅ **Procesamiento** — Quién, cuándo, cómo

---

### 4. Independencia

**Definición:** Cuántas fuentes independientes reportan lo mismo.

**Niveles:**

| Nivel | Descripción | Ejemplo |
|---|---|---|
| **PRIMARY** | Fuente original, directa | INE publica datos de desempleo |
| **SECONDARY_INDEPENDENT** | Fuente independiente confirma | El País reporta datos del INE |
| **SECONDARY_DEPENDENT** | Fuente dependiente (copia) | Blog copia artículo de El País |
| **TERTIARY** | Terciaria (múltiples copias) | Redes sociales comparten blog |

**Cálculo de independencia:**

```
Fuentes que reportan "Desempleo 25%":
- INE (PRIMARY) → cuenta como 1.0
- El País (SECONDARY_INDEPENDENT) → cuenta como 0.5
- El Mundo (SECONDARY_INDEPENDENT) → cuenta como 0.5
- Blog A (SECONDARY_DEPENDENT de El País) → cuenta como 0.1
- Blog B (SECONDARY_DEPENDENT de El País) → cuenta como 0.1

Independencia total = 1.0 + 0.5 + 0.5 + 0.1 + 0.1 = 2.1
→ "Múltiples fuentes independientes" (independence_count = 2)
```

**Importancia:** 5 copias ≠ 5 evidencias independientes.

---

### 5. Evidencia

**Definición:** Observación evaluada por calidad, independencia, corroboración.

**Evaluación de evidencia:**

```
Calidad = f(calidad_fuente, independencia, corroboración, contradicción)

Donde:
- calidad_fuente: 0-1 (VERIFIED_HIGH = 0.9, UNVERIFIED = 0.3)
- independencia: 1 + log(independence_count)
- corroboración: número de fuentes independientes que confirman
- contradicción: número de fuentes independientes que contradicen

Ejemplo:
- calidad_fuente = 0.9 (INE, oficial)
- independencia = 1 + log(2) = 1.3
- corroboración = 2 (INE + El País)
- contradicción = 0

Calidad = 0.9 × 1.3 × (2 / (2 + 0)) = 1.17 → normalizado a 0.95
```

**Tipos de evidencia:**

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **DIRECT_OBSERVATION** | Observación directa | Sensor mide temperatura |
| **DOCUMENTARY** | Documento oficial | INE publica datos |
| **STATISTICAL** | Análisis estadístico | Regresión, correlación |
| **EXPERT_TESTIMONY** | Testimonio de experto | Economista analiza datos |
| **PHYSICAL** | Evidencia física | Muestra de agua contaminada |
| **DIGITAL** | Evidencia digital | Logs, metadatos |
| **CIRCUMSTANTIAL** | Indirecta, contextual | Patrón de comportamiento |
| **ANALOGICAL** | Por analogía | Similar a caso histórico |

---

### 6. Corroboración

**Definición:** Múltiples evidencias independientes confirman la misma afirmación.

**Cálculo:**

```
Corroboración = número de fuentes independientes que confirman

Ejemplo:
- INE: "Desempleo 25%"
- El País: "Desempleo 25% (según INE)"
- Eurostat: "Desempleo 24% en Ceuta"

Corroboración = 3 (INE, El País, Eurostat)
Convergencia = 0.95 (25% vs 24% es consistente)
```

**Corroboración fuerte:**

- ✅ Múltiples fuentes independientes
- ✅ Múltiples métodos (estadístico, observacional, testimonial)
- ✅ Múltiples dominios (económico, social, político)

---

### 7. Contradicción

**Definición:** Evidencia que contradice la afirmación.

**Ejemplo:**

```
Afirmación: "Desempleo 25% en Ceuta"

Evidencia contradictoria:
- Estudio académico: "Desempleo real es 20% (economía sumergida no contada)"
- Sindicato: "Desempleo es 30% (datos oficiales subestimados)"

Contradicción = 2 fuentes independientes
Incertidumbre = 0.30 (discrepancia significativa)
```

**Manejo de contradicción:**

- ✅ Identificar fuentes contradictorias
- ✅ Evaluar calidad de cada fuente
- ✅ Calcular incertidumbre resultante
- ✅ Representar múltiples estimaciones (rango, no punto único)

---

### 8. Hipótesis

**Definición:** Explicación propuesta para fenómeno observado.

**Estructura:**

```
Hipótesis: "Aumento de desempleo causa aumento de polarización"

Componentes:
- Antecedente: "Aumento de desempleo"
- Consecuente: "Aumento de polarización"
- Mecanismo: "Estrés económico → hostilidad intergrupal"
- Predicciones: 
  - Si desempleo ↑, entonces polarización ↑
  - Si desempleo ↓, entonces polarización ↓
  - Controlando por otros factores, relación persiste
```

**Evaluación de hipótesis:**

- ✅ **Poder explicativo** — ¿Cuánta evidencia explica?
- ✅ **Consistencia** — ¿Es internamente consistente?
- ✅ **Coherencia** — ¿Es coherente con conocimiento establecido?
- ✅ **Simplicidad** — ¿Es parsimoniosa?
- ✅ **Falsabilidad** — ¿Es testable?

---

### 9. Hipótesis Alternativas

**Definición:** Hipótesis competidoras que explican el mismo fenómeno.

**Ejemplo:**

```
Fenómeno: Aumento de polarización en Ceuta

Hipótesis A: "Causa económica"
- Mecanismo: Desempleo → estrés → hostilidad
- Evidencia a favor: Correlación desempleo-polarización (r=0.7)
- Evidencia en contra: Polarización ↑ en grupos con empleo
- Probabilidad: 0.40

Hipótesis B: "Causa sociológica"
- Mecanismo: Segregación residencial → eco chambers → polarización
- Evidencia a favor: Correlación segregación-polarización (r=0.8)
- Evidencia en contra: Polarización ↑ en áreas mixtas
- Probabilidad: 0.50

Hipótesis C: "Causa política"
- Mecanismo: Discursos polarizantes → hostilidad
- Evidencia a favor: Análisis de contenido muestra ↑ hostilidad en discursos
- Evidencia en contra: Polarización ↑ antes de discursos
- Probabilidad: 0.30

Hipótesis D: "Multicausal"
- Mecanismo: Económico + sociológico + político interactúan
- Evidencia a favor: Modelo multivariante explica 80% de varianza
- Evidencia en contra: Complejo, difícil de testar
- Probabilidad: 0.70

Hipótesis preferida: D (mejor poder explicativo, aunque más compleja)
```

**Actualización bayesiana:**

```
Prior: P(A)=0.25, P(B)=0.25, P(C)=0.25, P(D)=0.25

Evidencia 1: Correlación segregación-polarización fuerte
- Likelihood: P(E1|A)=0.3, P(E1|B)=0.8, P(E1|C)=0.2, P(E1|D)=0.7
- Posterior: P(A|E1)=0.15, P(B|E1)=0.40, P(C|E1)=0.12, P(D|E1)=0.33

Evidencia 2: Modelo multivariante explica 80%
- Likelihood: P(E2|A)=0.4, P(E2|B)=0.5, P(E2|C)=0.3, P(E2|D)=0.9
- Posterior: P(A|E2)=0.12, P(B|E2)=0.32, P(C|E2)=0.09, P(D|E2)=0.47

Hipótesis D ahora tiene probabilidad 0.47 (la más alta)
```

---

### 10. Indicadores

**Definición:** Métricas cuantitativas que operacionalizan conceptos.

**Ejemplo:**

```
Concepto: "Polarización"

Indicadores:
- Hostilidad intergrupal (escala 1-10, encuesta)
- Segregación discursiva (índice 0-1, análisis de redes)
- Concentración de posiciones extremas (% en extremos)
- Afective polarization (diferencia en rating de grupos)
- Dehumanización frequency (% de lenguaje deshumanizante)

Cálculo compuesto:
Polarización_index = 0.3×hostilidad + 0.25×segregación + 0.2×extremismo + 0.15×affective + 0.1×dehumanización
```

**Propiedades de buenos indicadores:**

- ✅ **Válido** — Mide lo que pretende medir
- ✅ **Fiable** — Consistente en el tiempo
- ✅ **Sensible** — Detecta cambios
- ✅ **Específico** — No confundido por otros factores
- ✅ **Transparente** — Metodología clara, reproducible

---

### 11. Evolución

**Definición:** Cómo cambia el conocimiento con nueva evidencia.

**Tipos de evolución:**

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Refinamiento** | Confianza aumenta, rango se estrecha | Desempleo: 23-25% → 24-25% |
| **Revisión** | Confianza disminuye, rango se amplía | Desempleo: 24-25% → 20-30% |
| **Inversión** | Hipótesis preferida cambia | Económica → Multicausal |
| **Resolución** | Incertidumbre se resuelve | 20-30% → 25% (nuevo dato oficial) |

**Historial de evolución:**

```
Afirmación: "Desempleo en Ceuta"

2026-06-01: INE reporta 23%
- Confianza: 0.90
- Incertidumbre: 0.10

2026-09-01: INE reporta 25%
- Confianza: 0.90
- Incertidumbre: 0.10
- Cambio: +2% (tendencia ↑)

2026-09-15: Eurostat reporta 24%
- Confianza: 0.85 (discrepancia)
- Incertidumbre: 0.15
- Rango: 24-25%

2026-10-01: Estudio académico estima 20% (economía sumergida)
- Confianza: 0.70 (fuentes contradictorias)
- Incertidumbre: 0.30
- Rango: 20-25%
```

---

### 12. Probabilidad

**Definición:** Grado de confianza racional en hipótesis/afirmación.

**Interpretación bayesiana:**

- ✅ **Probabilidad = grado de confianza** (no frecuencia)
- ✅ **Actualiza con evidencia** (fórmula de Bayes)
- ✅ **Subjetiva pero racional** (restringida por coherencia lógica)

**Escalas:**

| Probabilidad | Interpretación | Ejemplo |
|---|---|---|
| **0.90 - 1.00** | Muy alta confianza | "Desempleo ~24%" (INE) |
| **0.70 - 0.90** | Alta confianza | "Polarización ↑" (múltiples indicadores) |
| **0.50 - 0.70** | Confianza moderada | "Causa multicausal" |
| **0.30 - 0.50** | Baja confianza | "Predicción: polarización ↑↑" |
| **0.00 - 0.30** | Muy baja confianza | "Hipótesis marginal" |

---

### 13. Confianza

**Definición:** Probabilidad combinada con calidad de evidencia.

**Cálculo:**

```
Confianza = Probabilidad × Calidad_evidencia

Donde:
- Probabilidad: 0-1 (bayesiana)
- Calidad_evidencia: 0-1 (fuente, independencia, corroboración)

Ejemplo:
- Probabilidad: 0.80 (hipótesis bien soportada)
- Calidad_evidencia: 0.90 (fuentes oficiales, múltiples, independientes)
- Confianza: 0.80 × 0.90 = 0.72
```

**Interpretación:**

- ✅ **Alta confianza** (≥0.70) — Acción justificada
- ✅ **Confianza moderada** (0.40-0.70) — Monitoreo, precaución
- ✅ **Baja confianza** (<0.40) — Incertidumbre alta, no actuar

---

### 14. Incertidumbre

**Definición:** Lo que no sabemos, o no sabemos con confianza.

**Tipos de incertidumbre:**

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Epistémica** | Falta de conocimiento | No hay datos de economía sumergida |
| **Aleatoria** | Inherentemente estocástica | Comportamiento individual |
| **Metodológica** | Limitaciones de método | Encuestas con sesgo de muestra |
| **Modelo** | Incertidumbre sobre modelo correcto | ¿Económica vs sociológica? |
| **Paramétrica** | Incertidumbre sobre parámetros | Tasa exacta de desempleo |

**Representación:**

```
Afirmación: "Desempleo en Ceuta es 20-25%"
- Estimación puntual: 22.5%
- Incertidumbre: ±2.5% (intervalo de confianza 95%)
- Tipo: Paramétrica + Epistémica

Afirmación: "Causa de polarización es multicausal"
- Probabilidad: 0.70
- Incertidumbre: 0.30
- Tipo: Modelo + Epistémica
```

**Principio de incertidumbre:**

> **Siempre reportar incertidumbre explícitamente.**

- ✅ No decir "X es Y" → Decir "X es Y con confianza Z"
- ✅ No ocultar incertidumbre → Hacerla explícita
- ✅ No sobre-precisar → Usar rangos, no puntos únicos

---

## 📊 Estados Epistemológicos

### Enum: `epistemic_state`

```sql
CREATE TYPE epistemic_state AS ENUM (
    'FACT_DOCUMENTED',           -- Hecho documentado (datos oficiales)
    'DECLARATION',               -- Declaración de fuente (no verificada)
    'EVIDENCE_SUPPORTED',        -- Evidencia soporta afirmación
    'EVIDENCE_CONTRADICTED',     -- Evidencia contradice afirmación
    'INFERENCE',                 -- Inferencia lógica
    'HYPOTHESIS',                -- Hipótesis (explicación propuesta)
    'ALTERNATIVE_HYPOTHESIS',    -- Hipótesis alternativa
    'UNCERTAIN',                 -- Incierto (evidencia mixta)
    'DISPROVEN',                 -- Refutado (evidencia fuerte en contra)
    'RETRACTED'                  -- Retirado (fuente se retractó)
);
```

### Criterios de Asignación

| Estado | Criterio | Ejemplo |
|---|---|---|
| **FACT_DOCUMENTED** | Datos oficiales, registros, estadísticas | "Desempleo 25% (INE)" |
| **DECLARATION** | Afirmación de fuente, no verificada | "Gobierno anuncia plan" |
| **EVIDENCE_SUPPORTED** | Múltiples evidencias independientes soportan | "Polarización ↑ (3 estudios)" |
| **EVIDENCE_CONTRADICTED** | Evidencia fuerte contradice | "Crimen ↓ (datos oficiales)" vs "Crimen ↑ (encuestas)" |
| **INFERENCE** | Inferencia lógica de hechos | "Si desempleo ↑ y servicios ↓, entonces estrés ↑" |
| **HYPOTHESIS** | Explicación propuesta, evidencia preliminar | "Causa es económica" |
| **ALTERNATIVE_HYPOTHESIS** | Hipótesis competidora | "Causa es sociológica" |
| **UNCERTAIN** | Evidencia mixta, no concluyente | "Efecto es ambiguo" |
| **DISPROVEN** | Evidencia fuerte refuta | "Hipótesis refutada por estudio controlado" |
| **RETRACTED** | Fuente se retracta | "Gobierno retracta afirmación" |

---

## 🔢 Cálculo de Confianza e Incertidumbre

### Fórmula de Confianza

```
Confianza = Probabilidad × Calidad_evidencia × Independencia × (1 - Incertidumbre)

Donde:
- Probabilidad: 0-1 (bayesiana)
- Calidad_evidencia: 0-1 (fuente, independencia, corroboración)
- Independencia: min(1, log(independence_count + 1))
- Incertidumbre: 0-1 (discrepancia entre fuentes, métodos, modelos)

Ejemplo:
- Probabilidad: 0.80
- Calidad_evidencia: 0.90
- Independencia: log(3 + 1) = 0.60 → min(1, 0.60) = 0.60
- Incertidumbre: 0.20

Confianza = 0.80 × 0.90 × 0.60 × (1 - 0.20) = 0.35
```

### Fórmula de Incertidumbre

```
Incertidumbre = w1×Discrepancia_fuentes + w2×Discrepancia_métodos + w3×Incertidumbre_modelo

Donde:
- Discrepancia_fuentes: desviación estándar entre estimaciones de fuentes
- Discrepancia_métodos: desviación estándar entre métodos
- Incertidumbre_modelo: incertidumbre sobre modelo correcto (0-1)
- w1, w2, w3: pesos (suma = 1)

Ejemplo:
- Discrepancia_fuentes: 0.15 (25% vs 24% vs 20%)
- Discrepancia_métodos: 0.10 (encuesta vs registro)
- Incertidumbre_modelo: 0.30 (¿económica vs sociológica?)
- Pesos: w1=0.4, w2=0.3, w3=0.3

Incertidumbre = 0.4×0.15 + 0.3×0.10 + 0.3×0.30 = 0.18
```

---

## 🎯 Aplicación a Dominios

### Ejemplo: Dominio ECONOMIC_SOCIAL

**Fenómeno:** Aumento de desempleo en Ceuta

**Cadena epistemológica:**

```
1. OBSERVACIÓN:
   - Texto: "Desempleo en Ceuta aumenta del 23% al 25% en Q3 2026"
   - Fuente: INE
   - Tipo: STATE
   - Dominio: ECONOMIC_SOCIAL

2. FUENTE:
   - Nombre: INE
   - Tipo: GOVERNMENT_OFFICIAL
   - Calidad: VERIFIED_HIGH
   - Independencia: PRIMARY

3. EVIDENCIA:
   - Calidad: 0.95 (fuente oficial)
   - Independencia: 1.0 (PRIMARY)
   - Corroboración: 2 (INE + El País)
   - Contradicción: 1 (Eurostat: 24%)

4. AFIRMACIÓN:
   - Texto: "Desempleo en Ceuta es 25%"
   - Estado: FACT_DOCUMENTED
   - Confianza: 0.90
   - Incertidumbre: 0.10

5. HIPÓTESIS:
   - Título: "Aumento de desempleo causa aumento de polarización"
   - Tipo: CAUSAL
   - Probabilidad: 0.60
   - Evidencia a favor: Correlación r=0.7
   - Evidencia en contra: Polarización ↑ en grupos con empleo

6. INDICADORES:
   - Tasa de desempleo: 25% (↑ 2%)
   - Polarización index: 0.65 (↑ 0.10)
   - Correlación: r=0.7, p<0.05

7. RIESGO:
   - Probabilidad: 0.60
   - Impacto: 4 (alto)
   - Vulnerabilidad: 0.70
   - Risk score: 0.60 × 4 × 0.70 = 1.68

8. ALERTA:
   - Nivel: WARNING
   - Dominio: ECONOMIC_SOCIAL + SOCIOLOGICAL_POLARIZATION
   - Explicación: "Desempleo ↑ correlaciona con polarización ↑"
```

---

## 📝 Principios de Implementación

### 1. Trazabilidad Completa

> **Toda afirmación debe trazarse a su fuente original.**

```
Afirmación → Evidencia → Observación → Documento → Fuente
```

### 2. Incertidumbre Explícita

> **Nunca ocultar incertidumbre.**

- ✅ Decir "25% (±2%, confianza 0.90)"
- ❌ No decir "25%" (sin incertidumbre)

### 3. Hipótesis Múltiples

> **Siempre considerar hipótesis alternativas.**

- ✅ Generar 3-5 hipótesis competidoras
- ✅ Evaluar cada una con evidencia
- ✅ Actualizar probabilidades con Bayes

### 4. Búsqueda Activa de Contradicción

> **Buscar evidencia que contradice, no solo confirma.**

- ✅ "¿Qué evidencia refutaría esta hipótesis?"
- ❌ No solo "¿Qué evidencia confirma esta hipótesis?"

### 5. Actualización Continua

> **Nueva evidencia → actualizar confianza.**

- ✅ Re-evaluar con cada nueva fuente
- ✅ Ajustar probabilidades (Bayes)
- ✅ Revisar hipótesis preferida

---

## 📚 Relacionados

- [Database Schema](../architecture/database-schema.md) — Tablas `claims`, `hypotheses`, `evidences`, etc.
- [API Documentation](../apis/public.md) — Endpoints que exponen estado epistemológico
- [Security Policy](../../SECURITY.md) — Integridad epistemológica, prevención de manipulación

---

*Modelo epistemológico vivo. Actualizar con cada avance en comprensión.*

**Última actualización:** Septiembre 2026  
**Versión:** 2.0.0
```

***#

***