### Session 6 (23-04-2026)

**Objetivo:**
Completar la integración modular de APIs externas, sistema de feature flags centralizado y gestión multiplataforma (CLI, API, SPA).

**Acciones realizadas:**
- Implementación de `ExternalAPIClient` en `src/core/external_api.py`.
- Integración de cliente externo en `CoreEngine` y exposición vía `call_external_api`.
- Endpoint `/external_api` en FastAPI y comando CLI para pruebas.
- Sistema de feature flags centralizado en YAML, editable desde CLI, API y SPA.
- SPA minimalista para gestión visual de flags, servida por FastAPI.
- CLI robusto: menú interactivo, gestión de flags, lanza SPA/API automáticamente.
- Tests unitarios y de integración para API, CLI y feature flags.
- Documentación y ejemplos actualizados en README y docs/.

**Resultados clave:**
- Todos los tests pasan en local y Docker.
- Cambios de flags se reflejan en todas las interfaces.
- SPA y CLI robustos y multiplataforma.

**Aprendizajes:**
- Centralizar la configuración de flags en YAML simplifica la gestión cross-interface.
- Automatizar el lanzamiento y cierre de API desde CLI mejora la UX.
- Validar siempre en Docker y local para robustez multiplataforma.
- La documentación y los tests son críticos para mantener la calidad.

**Próximos pasos:**
- Controlar sistema operativo (archivos, apps, red, etc.) (0.4.3).
- Crear versión Desktop (GUI) (0.5.0).
- Integrar LLM y Voice LLM para procesamiento avanzado (0.6.x).
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

### Session 4 (17-04-2026)
- Se analizaron errores concretos de v2 sobre el test set
- Se ampliaron ejemplos en clases problemáticas: ac_on/ac_off, tv_on/tv_off, open_app/close_app, volume_up/volume_down, lock/unlock
- Se creó una v3 experimental y una consola interactiva en src/chat_nox.py
- Se verificó que v3 quedó entrenada y exportada como models/intent_model_v3.joblib

**Resultados clave:**
- Dataset ampliado: 170 ejemplos
- v2 sobre dataset ampliado: 0.7059
- v3 sobre dataset ampliado: 0.7059
- La consola interactiva funciona y detecta intenciones por texto

**Aprendizajes:**
- Agregar datos sin revisar cuidadosamente el split puede bajar la métrica global
- El archivo .joblib solo existe si el entrenamiento ya se ejecutó y se exportó
- NOX hoy es un prototipo de NLU, no un asistente completo

**Próximos pasos:** fijar un split reproducible para comparar versiones sobre el mismo conjunto y luego entrenar una v4 basada en errores reales

### Session 5 (23-04-2026)

**Objetivo:**
Iniciar integración REST API para exponer el modelo y permitir interacción externa.

**Acciones realizadas:**
- Diseño de endpoints iniciales (`/predict_intent`, `/extract_entities`).
- Selección de framework: FastAPI.
- Implementación de estructura base en `src/api/`.
- Primeros tests locales con Uvicorn.
- Actualización de dependencias (`requirements.txt`).
- Documentación inicial en `docs/runbooks/api_rest.md`.

**Resultados clave:**
- API básica corriendo localmente.
- Endpoints funcionales para predicción y extracción de entidades.

**Problemas encontrados:**
- Pendiente: CORS, autenticación, serialización avanzada.

**Aprendizajes:**
- FastAPI facilita documentación automática y pruebas interactivas.
- Importancia de mantener la lógica desacoplada del CLI.

**Próximos pasos:**
- Añadir autenticación y CORS.
- Pruebas unitarias y e2e.
- Documentar endpoints y contrato.

**Notas:**
- Archivos nuevos: `src/api/main.py`, `docs/runbooks/api_rest.md`.
- Referencia a cambios en roadmap (0.4.1).

---

## ⚠️ Problemas Encontrados
- Dataset inicial desbalanceado en varias intenciones
- Algunas clases tienen soporte 1 en test, lo que reduce estabilidad de métricas
- Accuracy base aceptable para arranque, pero insuficiente para uso productivo
- La ampliacion de dataset cambio el comportamiento del split y redujo la comparabilidad directa con metricas anteriores

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
- [x] Consola interactiva de NOX implementada
- [x] Modelo v3 entrenado y validado

---

## 🚀 En Progreso
- [ ] Estabilizar comparacion entre versiones con el mismo split de evaluacion
- [ ] Diseñar v4 guiada por errores reales y no solo por ampliar datos

---

## 📝 Notas para el siguiente Agent
- El usuario entiende MLOps vs LLMOps
- Objetivo es crear algo producción-ready
- Importante: reentrenamiento periódico
- Futuro: integración con servicios de voz
- Mantener flujo pedagógico: explicar primero, ejecutar con OK del usuario y luego revisar resultados
