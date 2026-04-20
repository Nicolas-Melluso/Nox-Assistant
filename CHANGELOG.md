# Changelog

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
