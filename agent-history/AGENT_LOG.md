# 🤖 Custom Voice Assistant - Agent History Log

**Fecha de inicio:** 17 de Abril de 2026  
**Objetivo:** Crear un asistente virtual inteligente desde cero (MLOps → LLMOps)

---

## 📋 Decisiones Iniciales

### Objetivo del Usuario
Crear un asistente virtual personalizado que:
- Entienda comandos de voz (intent classification)
- Se integre con Google Home, Alexa y servicios personalizados
- Pueda ejecutar acciones basadas en intenciones
- Sea reentrenable periódicamente con nuevos datos

### Preferencias
- **Dataset:** Partir de base existente, luego entrenar periódicamente
- **Enfoque:** Completo (MLOps) - todo el pipeline
- **Carrera:** Ser ingeniero en este tema

---

## 🗺️ Roadmap del Proyecto

### Fase 1: Fundamentos ML (AQUÍ ESTAMOS)
- [ ] Crear modelo de clasificación de intenciones
- [ ] Dataset inicial con ejemplos de comandos
- [ ] Entrenamiento y evaluación
- [ ] Pipeline completo de datos

### Fase 2: Mejoras NLP
- [ ] Extracción de entidades (Entity Recognition)
- [ ] Procesamiento de lenguaje natural (spaCy/NLTK)
- [ ] Manejo de frases similares (sinonimia)

### Fase 3: Sistema de Acciones
- [ ] Conectar con APIs (Google Home, Alexa)
- [ ] Sistema de ejecución de tareas

### Fase 4: LLMOps
- [ ] Fine-tuning de LLMs
- [ ] Incorporar PromptFlow
- [ ] Monitoreo y evaluación continua

---

## 📁 Estructura del Proyecto

```
custom-voice-assistant/
├── agent-history/        # Este archivo y futuras notas
├── src/                  # Código principal
│   ├── data_pipeline.py  # Preparación de datos
│   ├── model.py          # Entrenamiento
│   ├── evaluate.py       # Evaluación
│   └── predict.py        # Predicciones
├── data/                 # Datasets
│   ├── raw/              # Datos sin procesar
│   ├── processed/        # Datos procesados
│   └── train_test/       # Train/Test split
├── models/               # Modelos entrenados
├── requirements.txt      # Dependencias
└── README.md             # Documentación
```

---

## 🔧 Dependencias Principales
- scikit-learn (ML)
- pandas, numpy (Data)
- spaCy (NLP)
- pickle (Model serialization)
- pytest (Testing)

---

## 💡 Notas y Aprendizajes

### Session 1 (17-04-2026)
- Usuario tiene clara visión del objetivo final
- Prefiere aprendizaje completo e integral
- Sistema de Agent History implementado para continuidad

**Próximos pasos:** Crear dataset inicial y primer modelo

---

## ⚠️ Problemas Encontrados
(Se actualizará conforme avancemos)

---

## ✅ Completado
- [x] Estructura del proyecto creada
- [x] Agent History system implementado

---

## 🚀 En Progreso
- [ ] Dataset inicial

---

## 📝 Notas para el siguiente Agent
- El usuario entiende MLOps vs LLMOps
- Objetivo es crear algo producción-ready
- Importante: reentrenamiento periódico
- Futuro: integración con servicios de voz
