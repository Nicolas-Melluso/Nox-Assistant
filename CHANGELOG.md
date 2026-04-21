# Changelog

## [0.3.2] - 2026-04-21
- Mejora de desambiguación contextual: extracción precisa de colores junto a dispositivos, evita duplicados de entidades MODO/MODO_TIPO y reglas más robustas para frases compuestas.
- Tests unitarios y modo interactivo validados localmente y en Docker.
- Documentación y ejemplos actualizados.

## [0.3.1] - 2026-04-21
- Integración de NLTK para limpieza avanzada de texto y análisis de sentimiento.
- Nuevas funciones: limpieza_avanzada y analizar_sentimiento en el pipeline.
- Documentación actualizada con comandos Docker definitivos para build, test y coverage.

## [0.3.0] - 2026-04-21
- Extracción avanzada de cantidades y unidades: soporta fracciones, palabras numéricas, docenas, expresiones complejas y edge cases.
- Validación exhaustiva: todos los tests y el modo interactivo funcionan igual en local y Docker.
- Documentación ampliada en README con ejemplos y comandos multiplataforma.

## [0.2.13] - 2026-04-21
- Integración de métricas automáticas de F1/precision/recall para intents sobre dataset real.
- Reportes generados en CSV y Markdown para análisis y documentación.
- Test de integración automatizado: valida accuracy mínima y paths robustos desde cualquier directorio.
- Documentación y ejemplos de uso actualizados.

## [0.2.12] - 2026-04-21
- Limpieza de dependencias en requirements.txt: solo quedan librerías realmente usadas.
- Validación completa: tests y modo interactivo funcionan localmente y en Docker.
- Documentación y CI actualizados.

## [0.2.11] - 2026-04-21
### Automatización de validación y CI
- Se agregó workflow de GitHub Actions para integración continua:
	- Build de imagen Docker sin cache.
	- Ejecución de tests unitarios en contenedor.
	- Medición de cobertura de código (falla si es <80%).
	- Corre en cada push y pull request a master/main.

## [0.2.10] - 2026-04-21
### Validación multiplataforma y Docker
- Se agregó Dockerfile y docker-compose.yml para ejecutar y testear el sistema en cualquier OS (Linux, Windows, macOS).
- Instrucciones de uso y troubleshooting multiplataforma en README.md.
- Tests unitarios y pipeline validados en contenedor Docker (garantiza robustez multiplataforma).

## [0.2.9] - 2026-04-21
### Métricas
- Cobertura de código: 89% (coverage)
- Accuracy de extracción de entidades: 100% de los tests unitarios pasan (15/15)
- Documentación actualizada con resultados y cómo medir cobertura localmente.

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
