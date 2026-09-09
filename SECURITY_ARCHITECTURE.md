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