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

## Tests automáticos

- Los tests unitarios usan pytest y una fixture engine para instanciar CoreEngine.
- Ejecuta los tests desde la raíz del proyecto:
  ```bash
  pytest tests -q
  ```
- Si usas imports desde src/, asegúrate de que el sys.path esté configurado (ver conftest.py).

## Contribución
- Sube solo código y datasets crudos
- Los resultados y archivos generados están ignorados en `.gitignore`

## Licencia
MIT

> Nota: El modelo spaCy español (es_core_news_sm) reconoce entidades LOC (lugares), ORG (organizaciones), PER (personas) y MISC (varios), pero no fechas ni horas.
> Ahora la extracción de entidades incluye fechas y horas usando dateparser, además de personas, lugares y organizaciones con spaCy.
