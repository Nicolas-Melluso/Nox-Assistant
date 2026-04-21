# Changelog
## [0.2.7] - 2026-04-21
## [0.2.8] - 2026-04-21
### Documentación
- Se agregó documentación sencilla y útil en README.md y docs/README.md:
	- Instalación rápida y comandos principales
	- Capacidades resumidas
	- Ejemplos avanzados y edge cases
	- Troubleshooting y estructura del proyecto
	- Ejemplo de uso directo en Python


# Changelog
## [0.2.6] - 2026-04-20
### Mejoras
- Ampliada la cobertura de patrones para comandos y dispositivos: se agregaron variantes ortográficas, sinónimos, regionalismos, conjugaciones frecuentes y errores comunes para mejorar la robustez y recall de la extracción de entidades.
- Documentación actualizada con ejemplos de nuevas variantes reconocidas.

## [0.2.5] - 2026-04-20
### Refactorización
- Pipeline de extracción de entidades completamente modularizado: cada etapa ahora está en un archivo individual bajo `src/core/entity_pipeline/` (limpieza, segmentación, extracción, postprocesamiento, desambiguación, ensamblado, nlp_singleton, regexes).
- Eliminados imports circulares y mejorada la mantenibilidad.
- Todos los tests unitarios pasan tras la refactorización.

## [0.2.4] - 2026-04-20
### Mejoras
- Preguntas y negaciones agregadas
- Test unitarios ampliados
- Intents mejorados

## [0.2.3] - 2026-04-20
### Mejoras
- Desambiguación contextual de entidades: reglas para distinguir entre DISPOSITIVO y MODO según el contexto de la frase (ej: "modo televisor").
- Agregado el patrón "modo" como entidad MODO.
- Post-procesamiento para asegurar la detección de "volumen" como DISPOSITIVO.
- Reglas contextuales para colores, volumen, alarma, puerta, etc.
- Tests unitarios ampliados para cubrir casos ambiguos y desambiguación.

### Correcciones
- Ajuste de imports y robustez en la detección de entidades en frases complejas.

## [0.2.2] - 2026-04-20
### Mejoras
- Integración de sinonimia y variantes para comandos y dispositivos.
- Campo `canonical` en entidades para obtener la forma normalizada.
- Tests unitarios para sinonimia y variantes.

### Correcciones
- Normalización robusta de frases multi-palabra.

## [0.2.1] - 2026-04-20
### Mejoras
- Extracción de entidades robusta con spaCy y EntityRuler.
- Patrones superponibles para "DISPOSITIVO" y "COMANDO" (ambos pueden detectarse en la misma frase).
- Limpieza, normalización, lematización y stemming en el pipeline.
- Accuracy de extracción de entidades: 91.3% (medido por tests unitarios).
- Documentación actualizada con nuevas capacidades y ejemplos.

### Correcciones
- Solución de errores de importación y ejecución de tests.
- Mejor manejo de spans superpuestos en spaCy.

## [0.2.0] - 2026-04-15
- Primera versión funcional del pipeline de clasificación y extracción de entidades.
