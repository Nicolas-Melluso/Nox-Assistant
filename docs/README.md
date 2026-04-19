# Documentación técnica NOX

## Pipeline de entrenamiento y predicción

- `balance_intent_dataset.py`: Limpia y balancea el dataset de intenciones.
- `train_intent_classifier.py`: Entrena el modelo usando el dataset balanceado y guarda el modelo y vectorizador.
- `smoke_test_intent_classifier.py`: Carga el modelo y vectorizador, y predice intenciones para frases de ejemplo.
- `analyze_intent_balance.py`: Analiza la cantidad de ejemplos por intención.

## Cómo usar
1. Balancea el dataset:
   ```bash
   python z/t.py --balance_intent_dataset.py
   ```
2. Entrena el modelo:
   ```bash
   python z/t.py --train_intent_classifier.py
   ```
3. Corre el smoke test:
   ```bash
   python z/t.py --smoke_test_intent_classifier.py
   ```

## Archivos clave
- Dataset balanceado: `training/datasets/processed/intents_p99_balanced.csv`
- Modelo entrenado: `models/intent_model.joblib`
- Vectorizador: `training/datasets/processed/intent_vectorizer.joblib`

## Estado actual
- El modelo logra 100% de precisión en el smoke test.
- El pipeline es reproducible y modular.

## Tests automáticos

- Los tests usan pytest y una fixture engine definida en conftest.py.
- Ejecutar desde la raíz del proyecto:
  ```bash
  pytest tests -q
  ```
- El archivo conftest.py agrega src/ al sys.path para que los imports funcionen correctamente.
