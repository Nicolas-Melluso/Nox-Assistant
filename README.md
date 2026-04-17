# NOX - Custom Voice Assistant

Proyecto de ML para clasificacion de intenciones de voz. NOX escucha comandos en lenguaje natural y determina la intencion del usuario con alta precision.

## Estado actual

| Modelo | Intents | Accuracy |
|--------|---------|----------|
| v1 (LogReg baseline) | 19 | 0.7083 |
| v2 (LinearSVC) | 19 | 0.7917 |
| v3 (LinearSVC + balanced) | 21 | 0.7059 |
| **nox100_best** | **103** | **0.9995 avg (20 runs)** |

El modelo `nox100_best` fue entrenado en 20 iteraciones con distintas semillas. Accuracy minima: 0.9964, maxima: 1.0000.

## Fases del proyecto

| Fase | Estado | Descripcion |
|------|--------|-------------|
| Fase 1: Clasificacion de intenciones | ✅ Completa | TF-IDF + LinearSVC, 103 intents, feedback loop |
| Fase 2: Extraccion de entidades | 🔲 Pendiente | spaCy, valores numericos, nombres de dispositivos |
| Fase 3: Sistema de acciones | 🔲 Pendiente | Ejecucion real de comandos, integracion con APIs |
| Fase 4: LLMOps | 🔲 Pendiente | Fine-tuning, PromptFlow, monitoreo |

## Estructura del proyecto

```
├── src/                          # Modulos core (importables)
│   ├── data_pipeline.py          # Limpieza y split train/test
│   ├── model.py                  # Build y entrenamiento de pipelines
│   ├── evaluate.py               # Metricas: accuracy, reporte, confusion matrix
│   └── predict.py                # Prediccion de intenciones
│
├── scripts/                      # Scripts ejecutables
│   ├── run_phase1.py             # Automatizacion completa Fase 1
│   ├── chat_nox.py               # Consola interactiva con NOX
│   ├── apply_feedback.py         # Incorpora feedback al dataset
│   ├── generate_nox_100_dataset.py  # Genera el dataset de 103 intents
│   └── train_nox100_iterative.py # Benchmark 20 runs, guarda mejor modelo
│
├── data/
│   ├── raw/                      # Datasets fuente (versionados en git)
│   │   ├── intent_dataset.csv        # Dataset base (19-21 intents)
│   │   ├── nox_100_intents_catalog.csv  # Catalogo de 103 intents
│   │   ├── nox_100_intents_dataset.csv  # 1404 ejemplos para nox100
│   │   └── nox_feedback.csv          # Correcciones capturadas en chat
│   ├── processed/                # Generado automaticamente (ignorado en git)
│   └── train_test/               # Split generado automaticamente (ignorado en git)
│
├── models/                       # Modelos serializados (ignorados en git)
│   └── intent_model_nox100_best.joblib
│
├── results/
│   └── nox100_iterative_results.csv  # Resultados de las 20 runs
│
├── requirements.txt
└── README.md
```

## Setup

```bash
# Ir al proyecto
cd custom-voice-assistant

# Crear ambiente virtual (solo primera vez, requiere Python 3.10)
python -m venv .venv

# Activar
source .venv/Scripts/activate   # Git Bash / WSL en Windows
# .venv\Scripts\activate        # PowerShell/CMD

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Probar NOX en modo interactivo (modelo principal)

```bash
python scripts/chat_nox.py
# Por defecto usa nox100_best. Escribi una frase y NOX predice la intencion.
# Si la prediccion es incorrecta, podes corregirla y queda guardada en nox_feedback.csv
```

### Incorporar feedback y reentrenar

```bash
# Aplicar correcciones al dataset nox100
python scripts/apply_feedback.py --target nox100

# Reentrenar con benchmark de 20 runs
python scripts/train_nox100_iterative.py
```

### Regenerar el dataset nox100 desde cero

```bash
python scripts/generate_nox_100_dataset.py
```

### Entrenar modelos v1/v2/v3 (modelos exploratorios)

```bash
python scripts/run_phase1.py --version v2 --predict-text "enciende las luces"
```

## Tecnologia usada

- **scikit-learn**: TfidfVectorizer + LinearSVC pipeline
- **joblib**: serializacion de modelos
- **pandas / numpy**: manejo de datos
- **Python 3.10**
