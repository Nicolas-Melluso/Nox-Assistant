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
├── src/                  # Código principal
├── data/                 # Datasets
├── models/               # Modelos entrenados
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## 🚀 Quick Start

```bash
# 1. Crear ambiente virtual
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar pipeline
python src/data_pipeline.py
python src/model.py
python src/evaluate.py
```

## 📚 Para más información
Ver [agent-history/AGENT_LOG.md](agent-history/AGENT_LOG.md)
