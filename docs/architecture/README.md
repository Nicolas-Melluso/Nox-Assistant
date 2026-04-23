# Arquitectura v0.4.2

El asistente NOX ahora cuenta con una arquitectura modular y extensible:

- **ExternalAPIClient**: módulo central para integración de APIs externas (REST, IoT, etc.), inyectado en CoreEngine.
- **CoreEngine**: motor principal, expone `call_external_api` y gestiona la lógica NLU y entidades.
- **Feature Flags**: sistema centralizado en YAML, accesible y editable desde CLI, API y SPA.
- **Interfaces**:
	- **CLI**: menú interactivo, gestión de flags, lanza SPA/API automáticamente.
	- **API REST**: endpoints para NLU, entidades, flags y APIs externas.
	- **SPA**: gestión visual de flags, servida por FastAPI.

**Flujo de datos:**
Usuario → CLI/API/SPA → CoreEngine → ExternalAPIClient (si aplica) → Respuesta/Acción

**Ventajas:**
- Modularidad, extensibilidad y testabilidad.
- Configuración centralizada y consistente.
- Fácil integración de nuevas capacidades y servicios externos.
# Documentación de la arquitectura

Este directorio contendrá diagramas, descripciones y decisiones de arquitectura del asistente de voz NOX.

- Estructura de módulos
- Flujo de datos
- Integraciones

Agrega aquí los archivos relevantes para mantener la arquitectura documentada y actualizada.