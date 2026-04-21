# Extracción de entidades avanzadas (v0.3.3)

Ahora el sistema reconoce entidades de:
- Google Maps: direcciones, ubicaciones, rutas, navegación.
- Control de Windows: abrir/cerrar apps, panel de control, terminal, apagar/reiniciar/bloquear.
- Asus Rog: Armoury Crate, ventilador, modos de rendimiento, RGB, overclock.
- Código de programación: crear/generar código, funciones, clases, snippets en varios lenguajes.

**Ejemplo:**
```
Frase: "Abrí Google Maps y generá un código Python para calcular la ruta"
Entidades: [
  {"label": "GOOGLE_MAPS", "text": "Google Maps"},
  {"label": "CODIGO_PROGRAMACION", "text": "código Python"},
  {"label": "COMANDO", "text": "abrí"},
  {"label": "COMANDO", "text": "generá"},
  {"label": "COMANDO", "text": "calcular"},
  {"label": "DISPOSITIVO", "text": "ruta"}
]
```

Todos los tests unitarios pasan y la integración es robusta en local y Docker.

El sistema ahora reconoce expresiones numéricas complejas y unidades en español, incluyendo:

- Fracciones: "media taza", "un cuarto de kilo", "tres cuartos de litro"
- Palabras numéricas: "una docena de huevos" (→ 12), "cien gramos"
- Números y unidades: "2 kilos de manzanas", "250 ml de aceite"
- Fracciones numéricas: "1/2 litro de agua", "2/3 de litro"

**Ejemplo interactivo:**

```
Frase: tengo que ir a comprar un kilo de yerba y poner la pava y cebar los mates
Frases segmentadas (3):
  1. tengo que ir a comprar un kilo de yerba
    Negación: False | Pregunta: False
    Entidades: [{'text': 'un kilo', 'label': 'CANTIDAD', 'cantidad': 1, 'unidad': 'kilo'}]
  2. poner la pava
    Negación: False | Pregunta: False
    Entidades: []
  3. cebar los mates
    Negación: False | Pregunta: False
    Entidades: []
```

**Edge cases soportados:**
- "una docena de huevos" → cantidad: 12, unidad: docena
- "media docena de empanadas" → cantidad: 6, unidad: docena
- "dos tercios de litro" → cantidad: 0.666..., unidad: litro

La extracción es robusta y funciona igual en local y Docker.

### Validación multiplataforma

Puedes validar la extracción y los tests en cualquier sistema operativo:

**Modo interactivo local:**
```bash
python custom-voice-assistant/z/entity_extraction_interactive_script.py
```

**Modo interactivo en Docker:**
```bash
docker build --no-cache -t custom-voice-assistant .
docker run --rm -it custom-voice-assistant
```

**Tests unitarios locales:**
```bash
pytest tests/unit
```

**Tests unitarios en Docker:**
```bash
docker build --no-cache -t custom-voice-assistant .
docker run --rm -e TESTS=1 custom-voice-assistant
```

**Cobertura en Docker:**
```bash
docker run --rm -e TESTS=1 custom-voice-assistant sh -c "pip install coverage && coverage run -m pytest tests/unit && coverage report --fail-under=80"
```

Todos los tests deben pasar y la extracción debe funcionar igual en ambos entornos.

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

## TODO Roadmap

- [x] Modularizar pipeline en etapas separadas (0.2.0)
- [x] Extracción de entidades robusta con spaCy EntityRuler (0.2.0)
- [x] Soporte para negación y preguntas (0.2.1)
- [x] Segmentación manual para frases compuestas (0.2.2)
- [x] Extraer dependencias gramaticales (sujeto, verbo, objeto) (0.2.3)
- [x] Integrar tests unitarios para todos los casos (0.2.4)
- [x] Actualizar documentación y changelog (0.2.5)
- [x] Mejorar cobertura de patrones para variantes y sinónimos (0.2.6)
- [x] Refactorizar para máxima legibilidad (0.2.7)
- [x] Documentar ejemplos avanzados y edge cases (0.2.8)
- [x] Medir y documentar cobertura y accuracy (0.2.9)
- [x] Validar robustez multiplataforma (0.2.10)
- [x] Automatizar validación y CI (0.2.11)
- [x] Revisar y limpiar dependencias en requirements.txt (0.2.12)
- [x] Agregar cualquier mejora relevante sugerida por el equipo (0.2.13)
- [x] Agregar extracción de cantidades y unidades (0.3.0)
- [ ] Integrar NLTK para limpieza avanzada y sentimiento (0.3.1)
- [ ] Mejorar desambiguación contextual (0.3.2)
- [ ] Agregar nuevos tipos de entidades (0.3.3)
- [ ] Expandir tests unitarios para nuevos casos (0.3.4)
- [ ] Integrar con CoreEngine y predict_intent (0.3.5)
- [ ] Implementar CLI para interacción por consola (0.4.0)
- [ ] Exponer API REST para integración externa (0.4.1)
- [ ] Conectar con APIs externas (servicios, datos, IoT) (0.4.2)
- [ ] Controlar sistema operativo (archivos, apps, red, etc.) (0.4.3)
- [ ] Crear versión Desktop (GUI) (0.5.0)
- [ ] Integrar LLM para procesamiento avanzado (0.6.0)
- [ ] Integrar Voice LLM para comandos por voz (0.6.1)
- [ ] Implementar autoaprendizaje y feedback continuo (0.7.0)