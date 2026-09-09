# Contributing to CEUTIA

> **Guía exhaustiva para contribuir al sistema CEUTIA**
>
> *Sistema de Inteligencia Territorial para Salvar a la Humanidad*

---

## ⚠️ IMPORTANTE: Proyecto Privado y Propietario

**CEUTIA es un proyecto privado y propietario.**

- Solo pueden contribuir **miembros autorizados explícitamente**
- Todo el código es **confidencial**
- No se puede compartir externamente sin permiso escrito
- Las contribuciones están sujetas a la [Licencia](./LICENSE)

Si has recibido acceso a este repositorio, es porque has sido **explícitamente autorizado** por el propietario.

---

## 🎯 Propósito de esta Guía

Esta guía establece los estándares para contribuir a CEUTIA, asegurando:

- **Calidad técnica** — Código robusto, seguro, mantenible
- **Consistencia** — Estilo uniforme en todo el proyecto
- **Seguridad** — Protección de datos sensibles y secretos
- **Trazabilidad** — Todo cambio es auditable
- **Propósito alineado** — Contribuciones alineadas con la misión de salvar vidas

---

## 🌟 Principios Fundamentales

### 1. Evidencia antes que Narrativa

> **Los hechos documentados gobiernan.**

- No implementar funcionalidad basada en suposiciones
- Todo debe estar documentado o ser trazable a una fuente
- Si hay incertidumbre, hacerla explícita

### 2. Seguridad Primero

> **Nunca comprometer la seguridad por conveniencia.**

- Nunca subir secretos al repositorio
- Validar siempre inputs del usuario
- Usar parámetros preparados (no SQL injection)
- Encriptar datos sensibles
- Seguir principio de mínimo privilegio

### 3. Separación Estricta de Perímetros

> **Público, Owner y Médico son independientes.**

- No cruzar datos entre perímetros
- Módulo médico NUNCA se usa para inteligencia territorial
- Datos sensibles solo en Owner

### 4. Auditoría Completa

> **Todo cambio debe ser trazable.**

- Commits descriptivos
- Tests para funcionalidad crítica
- Logs de acciones importantes
- Documentar cambios significativos

### 5. Propósito Claro

> **Ayudar a la humanidad, no acumular datos.**

- Cada línea de código debe servir al propósito
- No implementar features "porque sí"
- Priorizar impacto sobre complejidad

---

## 🚀 Flujo de Trabajo

### 1. Crear Rama (Branch)

```bash
# Desde main, crear rama descriptiva
git checkout main
git pull origin main
git checkout -b feature/descripcion-corta
