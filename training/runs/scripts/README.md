# Entrenamiento y predicción de intenciones

Este módulo contiene scripts para entrenar y probar un clasificador de intenciones usando scikit-learn.

## Estructura principal
- `train_intent_classifier.py`: Entrena el modelo usando un dataset balanceado y guarda el modelo y vectorizador.
- `smoke_test_intent_classifier.py`: Carga el modelo y vectorizador, y predice intenciones para frases de ejemplo.
- `balance_intent_dataset.py`: Limpia y balancea el dataset de intenciones.
- `analyze_intent_balance.py`: Analiza la cantidad de ejemplos por intención.

## Cómo entrenar y probar
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

## Ubicación de archivos
- Dataset balanceado: `training/datasets/processed/intents_p99_balanced.csv`
- Modelo entrenado: `models/intent_model.joblib`
- Vectorizador: `training/datasets/processed/intent_vectorizer.joblib`

## Notas
- El pipeline está modularizado y documentado.
- El modelo actual logra 100% de precisión en el smoke test.
