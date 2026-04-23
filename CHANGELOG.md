# Changelog
## [v0.4.2] - 2026-04-23
- Integración modular de APIs externas vía ExternalAPIClient (src/core/external_api.py).
- CoreEngine expone call_external_api y lo integra en CLI, API y SPA.
- Sistema de feature flags centralizado (YAML), editable desde CLI, API y SPA.
- SPA minimalista para gestión visual de flags, servida por FastAPI.
- CLI robusto: menú interactivo, gestión de flags, lanza SPA/API automáticamente.
- Tests unitarios y de integración para API, CLI y feature flags.
- Documentación y ejemplos actualizados en README y docs/.
- Validación: todos los tests pasan en local y Docker.

## [v0.4.1] - 2026-04-23
- Expuesta API REST robusta con FastAPI y endpoints `/predict_intent` y `/extract_entities`.
- Documentación de API y ejemplos de uso en `docs/runbooks/api_rest.md` y README.md.
- CLI y API comparten lógica central (CoreEngine), garantizando resultados consistentes.
- Tests unitarios para API y CLI: parametrizados, robustos y con cobertura total (incluye modo no interactivo para CLI).
- Fix multiplataforma: imports y sys.path en tests y CLI para funcionar igual en Windows, Linux, Docker y CI.
- CLI ahora soporta modo test (`--once`) y es seguro en entornos no interactivos (sin Unicode en stdout si no hay TTY).
- Corrección de errores de encoding y timeout en tests de CLI (timeout aumentado para modelos grandes).
- Validación: todos los tests pasan en local y Docker, incluyendo API, CLI y core.
- Actualización de roadmap, runbooks y changelog.
- Mejoras menores de UX y mensajes de error en CLI y API.

## [v0.4.0] - 2026-04-23
- Banner CLI completamente rojo y soporte de colores ANSI.
- Ctrl+C ahora cierra el CLI de forma segura en cualquier terminal (no requiere doble Ctrl+C).
- Mejor integración multiplataforma (CMD, PowerShell, Bash, VS Code).
- Troubleshooting centralizado en `docs/runbooks/TROUBLESHOOTING.md`.

## [v0.3.6] - 2026-04-21
- Clasificación de intenciones ahora basada en embeddings (sentence-transformers) y similitud de coseno, con umbral ajustable para máxima precisión.
- Ejemplos de entrenamiento expandidos para distinguir intenciones similares ("create" vs "generate", "answer" vs "send").
- Ajuste automático: si la intención es "unknown", la confianza se reporta como 0.0.
- Nuevo: todas las frases no reconocidas o con baja confianza se guardan automáticamente en `errores_intencion.log` para futuros entrenamientos.
- Todos los tests unitarios pasan en local y Docker.
- Documentación y ejemplos actualizados en README.md.

## [v0.3.5] - 2026-04-21
- Todos los imports internos refactorizados a relativos para máxima robustez multiplataforma (funciona igual en local, Docker y cualquier entrypoint).
- Script interactivo de CoreEngine (`z/engine_interactive_test.py`) ahora funciona desde cualquier carpeta y en Docker.
- Validación completa: todos los tests unitarios pasan en local y Docker.
- Documentación y ejemplos de uso interactivo actualizados.


## [0.3.4] - 2026-04-21
- Tests unitarios expandidos para cubrir entidades avanzadas: GOOGLE_MAPS, CONTROL_WINDOWS, ASUS_ROG_CONTROL, CODIGO_PROGRAMACION.
- Se agregaron patrones compuestos para mejorar la extracción de entidades multi-palabra (ej: "Google Maps", "panel de control", "modo turbo").
- Todos los tests pasan en local y Docker.
- Documentación y ejemplos actualizados en README y docs/README.md.

## [0.3.3] - 2026-04-21
- Agregados nuevos tipos de entidades: GOOGLE_MAPS, CONTROL_WINDOWS, ASUS_ROG_CONTROL, CODIGO_PROGRAMACION.
- Refactor de imports y robustez en el pipeline de postprocesamiento.
- Todos los tests unitarios pasan y la integración es multiplataforma.

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

## [0.4.1] - 2026-04-23
### Añadido
- API REST inicial con FastAPI: endpoints /predict_intent y /extract_entities.
- Documentación de uso y ejemplos curl.
- Método extract_entities en CoreEngine.
- Runbook de API REST con tareas futuras.

### Mejorado
- Refactor de endpoints para devolver estructura completa y robusta.

### Próximos pasos
- Seguridad, rate limiting, autenticación, webhooks, pruebas e2e, desacoplar como microservicio.
