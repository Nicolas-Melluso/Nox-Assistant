# NOX - Custom Voice Assistant

Proyecto de asistente de voz para Windows con clasificación de intenciones en español, ejecución de acciones reales y arquitectura modular.

## Características principales
- Clasificación de intenciones con ML (scikit-learn, TF-IDF, Naive Bayes)
- Dataset balanceado y pipeline reproducible
- Enrutamiento robusto y extracción de entidades
- Ejecución de acciones locales en Windows
- Datasets crudos y procesados versionados

## Estructura del proyecto
- `src/` - Código fuente principal
- `training/runs/scripts/` - Scripts de entrenamiento, balanceo y smoke test
- `training/datasets/raw/` - Datasets crudos (versionados)
- `training/datasets/processed/` - Datasets balanceados y vectorizadores
- `models/` - Modelos entrenados
- `results/` - Resultados y logs
- `agent-history/` - Historial de sesiones (no versionado)

## Uso rápido
1. Instala dependencias: `pip install -r requirements.txt`
2. Balancea el dataset: `python z/t.py --balance_intent_dataset.py`
3. Entrena el modelo: `python z/t.py --train_intent_classifier.py`
4. Corre el smoke test: `python z/t.py --smoke_test_intent_classifier.py`

## Ubicación de archivos
- Dataset balanceado: `training/datasets/processed/intents_p99_balanced.csv`
- Modelo entrenado: `models/intent_model.joblib`
- Vectorizador: `training/datasets/processed/intent_vectorizer.joblib`

## Capacidades actuales de la IA

- Clasificación de intenciones en español usando ML (scikit-learn)
- Balanceo automático de dataset de intenciones
- Modularización del código (src/core/)
- Tests automáticos con pytest y fixture engine
- Extracción de entidades con spaCy (nombres, lugares, fechas, etc.) y dateparser
- Documentación técnica y de uso
- Pipeline reproducible y versionado

### Arquitectura modular del pipeline de entidades (2026-04-20)

El pipeline de extracción de entidades ha sido refactorizado y ahora cada etapa está separada en archivos individuales dentro de `src/core/entity_pipeline/`:

- `limpieza.py`: limpieza y normalización de texto
- `segmentacion.py`: segmentación de frases y oraciones
- `extraccion.py`: extracción base de entidades con spaCy
- `postprocesamiento.py`: post-procesamiento, sinonimia, fechas, horas, volumen
- `desambiguacion.py`: desambiguación contextual de entidades
- `ensamblado.py`: ensamblado del output estructurado
- `nlp_singleton.py`: inicialización única de spaCy y EntityRuler
- `regexes.py`: regexes para fechas y horas

Esto mejora la mantenibilidad, escalabilidad y claridad del código. Todas las funciones principales se importan desde estos submódulos en `entity_extraction.py`.

## Tests automáticos

- Los tests unitarios usan pytest y una fixture engine para instanciar CoreEngine.
- Ejecuta los tests desde la raíz del proyecto:
  ```bash
  pytest tests -q

  - Accuracy actual: **91.3%** en extracción de entidades (comando y dispositivo) sobre el set de pruebas unitarias.
  - Patrones independientes y superpuestos para `COMANDO` y `DISPOSITIVO` usando spaCy EntityRuler (ambos pueden detectarse en la misma frase, incluso si están solapados).
  - Pipeline robusto: limpieza, normalización, lematización y stemming.
  - Integración de sinonimia: comandos y dispositivos se normalizan a su forma canónica (campo `canonical` en la salida).
  - Ejemplo: frases como "Enciende la luz", "Prendé la lámpara" o "Actívalo" se normalizan a `prende` como comando canónico.

  Ejemplo:
  - Entrada: `Enciende las luces`
  - Salida: `[{"text": "Enciende las luces", "label": "COMANDO", "canonical": "prende"}, {"text": "luces", "label": "DISPOSITIVO", "canonical": "luz"}]`
```

```mermaid
graph TD
    A[Texto de usuario] --> B[CoreEngine.predict_intent]
    B --> C[Clasificador de intenciones]
    B --> D[Extracción de entidades (spaCy + dateparser)]
    C --> E[Intent]
    D --> F[Entities]
    E & F --> G[Ejecutor de acciones]
    G --> H[Respuesta/Acción]
```

### Ejemplo de flujo

1. Usuario: "Recordame el 10 de diciembre a las 18:00 con Juan Pérez en Madrid."
2. CoreEngine.predict_intent analiza el texto.
3. Se predice la intención (placeholder) y se extraen entidades (persona, lugar, fecha, hora).
4. El ejecutor de acciones recibe el intent y las entidades para decidir qué hacer.

## Comandos rápidos

### Ejecutar el script interactivo de extracción de entidades

Desde la raíz del proyecto:

```
python custom-voice-assistant/z/entity_extraction_interactive_script.py
```

### Ejecutar los tests unitarios

Desde la raíz del proyecto:

```
pytest custom-voice-assistant/tests/unit
```