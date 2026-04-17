# 🎙️ Custom Voice Assistant

Un proyecto completo de ML → LLMOps para crear un asistente virtual personalizado.

## 🎯 Objetivo

Construir un asistente de voz inteligente que:
- Clasifique intenciones de comandos de voz
- Extraiga entidades relevantes
- Ejecute acciones personalizadas
- Se integre con Google Home, Alexa y servicios custom
- Sea reentrenable periódicamente

## 📊 Fases del Proyecto

### ✅ Fase 1: Fundamentos ML (Actual)
- Clasificación de intenciones
- Dataset inicial
- Pipeline completo de datos

### 🔄 Fase 2: Mejoras NLP
- Entity Recognition
- Procesamiento de lenguaje natural
- Manejo de sinonimia

### 🔌 Fase 3: Sistema de Acciones
- Integración con APIs
- Sistema de ejecución

### 🚀 Fase 4: LLMOps
- Fine-tuning de LLMs
- PromptFlow
- Monitoreo y evaluación

## 📁 Estructura

```
├── agent-history/        # Historial de conversaciones con IA
├── src/                  # Código principal del pipeline ML
├── data/                 # Datasets (raw y generados)
├── models/               # Modelos entrenados exportados
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## 🧠 Qué hace cada archivo (Fase 1)

- src/data_pipeline.py: limpia texto, elimina duplicados y separa train/test.
- src/model.py: entrena el clasificador de intenciones (TF-IDF + Logistic Regression).
- src/evaluate.py: evalua el modelo con accuracy, reporte y matriz de confusion.
- src/predict.py: prueba predicciones de ejemplo con frases nuevas.
- src/run_phase1.py: ejecuta toda la Fase 1 con un solo comando.
- data/raw/intent_dataset.csv: dataset base editable por ti.
- models/intent_model.joblib: modelo entrenado (se genera despues de entrenar).

## 🔁 Flujo real de trabajo

1. Editas o amplias el dataset base en data/raw/intent_dataset.csv.
2. Corres data_pipeline.py para regenerar datos limpios y split train/test.
3. Corres model.py para entrenar y guardar el modelo.
4. Corres evaluate.py para medir calidad.
5. Corres predict.py para validar frases manuales.

Tambien puedes ejecutar todo junto con run_phase1.py.

## 🚀 Cómo correrlo paso a paso

```bash
# 1) Ir al proyecto
cd /c/Users/nicol/OneDrive/Documentos/Projects/ai-learning/custom-voice-assistant

# 2) Crear ambiente virtual (solo primera vez)
python -m venv .venv

# 3) Activar ambiente virtual
source .venv/Scripts/activate   # Git Bash en Windows
# .venv\Scripts\activate        # PowerShell/CMD en Windows
# source .venv/bin/activate      # Linux/Mac

# 4) Instalar dependencias
pip install -r requirements.txt

# 5) Ejecutar Fase 1 completa
python src/data_pipeline.py
python src/model.py
python src/evaluate.py
python src/predict.py

# 6) O ejecutar todo junto con una sola orden
python src/run_phase1.py --version v1

# 7) Entrenar la segunda version y probar una frase manual
python src/run_phase1.py --version v2 --predict-text "desbloquea la puerta del patio"
```

## 📌 Estado actual

- Fase 1 implementada (baseline funcionando).
- Accuracy inicial aproximada: 0.71.
- Accuracy v2 aproximada: 0.79.
- Siguiente mejora: balancear dataset por intencion para subir recall en clases con pocos ejemplos.
