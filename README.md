# Métricas automáticas de intents

El proyecto ahora integra un pipeline de métricas automáticas para intents:

- Evalúa F1, precisión y recall sobre el dataset real (`training/datasets/processed/intents_p99_balanced.csv`).
- Genera reportes en CSV y Markdown en `training/runs/csv/` (útiles para análisis y documentación).
- El test `test_metrics_integration.py` valida automáticamente la accuracy mínima y puede ejecutarse desde cualquier directorio.
- Los paths son robustos y funcionan tanto en local como en CI.

### Ejecución manual

```bash
python custom-voice-assistant/training/runs/scripts/eval_metrics.py
```

### Ejecución automática en tests

```bash
pytest custom-voice-assistant/tests/unit
```

### Ejemplo de reporte Markdown generado

| Intent | Precision | Recall | F1 | Soporte |
|--------|-----------|--------|----|---------|
| abrir_app | 0.111 | 1.000 | 0.200 | 150 |
| cerrar_app | 0.000 | 0.000 | 0.000 | 150 |
| ... | ... | ... | ... | ... |
| accuracy | - | - | 0.111 | - |

Puedes adaptar el pipeline para entidades siguiendo la misma estructura.
# 21/04/2026
- Se realizó una limpieza exhaustiva de dependencias en requirements.txt.
- Validado: todos los tests y el modo interactivo funcionan localmente y en Docker.
- El proyecto está listo para nuevas mejoras y expansión.

## Integración Continua (CI)

El proyecto cuenta con un workflow de GitHub Actions que valida automáticamente en cada push y pull request a `master`/`main`:

- Build de la imagen Docker sin cache.
- Ejecución de todos los tests unitarios dentro del contenedor.
- Medición de cobertura de código (falla si es menor al 80%).
- Verificación de que el archivo `CHANGELOG.md` esté actualizado respecto a la rama principal.

Esto garantiza calidad, reproducibilidad y documentación actualizada en cada entrega.

Puedes ver la configuración en `.github/workflows/ci.yml`.
# NOX - Custom Voice Assistant

Proyecto de asistente de voz para Windows con clasificación de intenciones en español, ejecución de acciones reales y arquitectura modular.


## Uso con Docker (validación multiplataforma)

Puedes correr y testear todo el sistema en un contenedor Docker, garantizando que funcione igual en Linux, Windows y macOS.

### Comandos definitivos multiplataforma

**Modo interactivo real (consola):**
```bash
docker build --no-cache -t custom-voice-assistant . && docker run --rm -it custom-voice-assistant
```
Esto reconstruye la imagen desde cero y lanza el modo interactivo real (requiere `-it` para entrada por consola).

**Modo testing (unit tests):**
```bash
docker build --no-cache -t custom-voice-assistant . && docker run --rm -e TESTS=1 custom-voice-assistant
```
Esto reconstruye la imagen y ejecuta todos los tests unitarios en el contenedor.

---

### Troubleshooting multiplataforma
- Si algún test falla en Docker y no en tu entorno local, revisa rutas relativas, permisos de archivos y dependencias del sistema.
- El contenedor instala todas las dependencias necesarias para spaCy y dateparser.
- Puedes montar tu código local con `-v $(pwd):/app` para desarrollo interactivo.

---

## Instalación rápida

1. Clona el repositorio:
  ```bash
  git clone https://github.com/tu_usuario/custom-voice-assistant.git
  cd custom-voice-assistant
  ```
2. Instala dependencias:
  ```bash
  pip install -r requirements.txt
  ```
3. (Opcional) Instala spaCy y el modelo español si no está:
  ```bash
  pip install spacy
  python -m spacy download es_core_news_sm
  ```

## Comandos principales

- Entrenar modelo: `python z/t.py --train_intent_classifier.py`
- Balancear dataset: `python z/t.py --balance_intent_dataset.py`
- Ejecutar pruebas: `pytest tests/unit -v`
- Ejecutar asistente: `python src/main.py`

## Capacidades principales

- Clasificación de intenciones en español (ML)
- Extracción robusta de entidades (spaCy + patrones custom)
- Reconocimiento de variantes, sinónimos y errores comunes
- Soporte para negaciones, preguntas, fechas, horas y dispositivos
- Modularidad y fácil extensión

## Ejemplos avanzados y edge cases

Frases que el sistema reconoce correctamente:

- "Prendé la luz del baño y apaga el ventiladorcito"
- "Pon la alarma a las 7:30 y despiértame después"
- "Subí el volumen del televisor y baja la música"
- "¿Puedes abrir la puerta y encender la alarma?"
- "Apaga la heladera y la nevera"
- "Configura el modo noche y baja el brillo"
- "¿Qué clima hace hoy?"
- "Pon la alarma en 5 minutos"

Edge cases:
- Frases con errores de tipeo: "prende la luz y apaga el ventiladro"
- Regionalismos: "enciende la nevera" (sinónimo de heladera)
- Comandos compuestos: "sube el volumen y baja la música"

## Troubleshooting

- Si spaCy no detecta entidades, asegúrate de tener el modelo `es_core_news_sm` instalado.
- Si hay errores de importación, ejecuta los comandos desde la raíz del proyecto.

## Cobertura y accuracy (0.2.9)

- **Cobertura de código:** 89% (medido con coverage)
- **Accuracy de extracción de entidades:** 100% de los tests unitarios pasan (15/15)
- Módulos principales (`src/core/entity_pipeline/`) con cobertura >85%

Puedes medir cobertura localmente con:
```bash
coverage run -m pytest tests/unit && coverage report
```

## Más información

Consulta la documentación en `docs/` para detalles de arquitectura, ejemplos, integración y buenas prácticas.

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
- Reconocimiento robusto de comandos y dispositivos con variantes, sinónimos, regionalismos y errores comunes (EntityRuler spaCy 0.2.6)
- Documentación técnica y de uso
- Pipeline reproducible y versionado

### Ejemplos de variantes reconocidas (0.2.6)

- "enciende", "prende", "activa", "enciéndeme", "prendé", "actívalo", "activalo"
- "apaga", "apagá", "desactiva", "apágame", "desactívalo", "desactivalo"
- "heladera", "nevera", "refrigerador", "frigorífico"
- "ventilador", "ventiladro", "ventiladorcito"
- "microondas", "microonda", "microodas"
- "timbre", "timber"
- "portero", "portero eléctrico"
- "pantalla", "pantallón", "monitor"
- "celular", "móvil", "smartphone"

Esto permite que el sistema entienda comandos y dispositivos aunque el usuario use variantes, errores o regionalismos.

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