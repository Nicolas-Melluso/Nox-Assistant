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
- [x] Crear modelo de clasificación de intenciones
- [x] Dataset inicial con ejemplos de comandos
- [x] Entrenamiento y evaluación
- [x] Pipeline completo de datos

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

### Session 2 (17-04-2026)
- Se creó dataset inicial con 120 ejemplos y 19 intenciones
- Se implementó pipeline de limpieza y split train/test (80/20)
- Se entrenó un clasificador base con TF-IDF + Logistic Regression
- Se ejecutó evaluación y script de predicción con ejemplos

**Resultados clave:**
- Accuracy inicial: 0.7083
- Clases fuertes: lights_on, lights_off, get_time, get_weather, set_temperature
- Clases débiles por poco soporte: ac_on/ac_off, tv_on/tv_off, close_app, unlock_door

**Próximos pasos:** balancear dataset (mínimo 12-20 ejemplos por intención) y reentrenar

### Session 3 (17-04-2026)
- Se corrigió el entorno virtual del proyecto recreandolo con Python 3.10
- Se versionó el entrenamiento para comparar v1 y v2
- Se creó una automatización de Fase 1 con run_phase1.py
- Se entrenó una v2 con TF-IDF más amplio y LinearSVC

**Resultados clave:**
- v1 accuracy: 0.7083
- v2 accuracy: 0.7917
- Mejora absoluta: 0.0834

**Intervenciones posibles del usuario:**
- Editar el dataset base
- Cambiar reglas de limpieza de texto
- Cambiar hiperparámetros del vectorizador
- Cambiar el algoritmo de clasificación

**Próximos pasos:** revisar confusion matrix, balancear clases débiles y crear una v3 orientada a datos

---

## ⚠️ Problemas Encontrados
- Dataset inicial desbalanceado en varias intenciones
- Algunas clases tienen soporte 1 en test, lo que reduce estabilidad de métricas
- Accuracy base aceptable para arranque, pero insuficiente para uso productivo

---

## ✅ Completado
- [x] Estructura del proyecto creada
- [x] Agent History system implementado
- [x] Dataset inicial creado
- [x] Pipeline de datos implementado
- [x] Modelo base entrenado
- [x] Evaluación inicial ejecutada
- [x] Script de predicción implementado
- [x] Automatización de Fase 1 implementada
- [x] Modelo v2 entrenado y comparado contra v1

---

## 🚀 En Progreso
- [ ] Balanceo de dataset para mejorar recall por intención
- [ ] Segunda iteración de entrenamiento (v2)

---

## 📝 Notas para el siguiente Agent
- El usuario entiende MLOps vs LLMOps
- Objetivo es crear algo producción-ready
- Importante: reentrenamiento periódico
- Futuro: integración con servicios de voz
- Mantener flujo pedagógico: explicar primero, ejecutar con OK del usuario y luego revisar resultados
