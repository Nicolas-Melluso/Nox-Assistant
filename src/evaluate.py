from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = PROJECT_ROOT / "data" / "train_test" / "test.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "intent_model.joblib"


def main() -> None:
    if not TEST_PATH.exists():
        raise FileNotFoundError("No existe test.csv. Ejecuta primero: python src/data_pipeline.py")

    if not MODEL_PATH.exists():
        raise FileNotFoundError("No existe el modelo. Ejecuta primero: python src/model.py")

    test_df = pd.read_csv(TEST_PATH)
    x_test = test_df["text"].astype(str)
    y_test = test_df["intent"].astype(str)

    model = joblib.load(MODEL_PATH)
    y_pred = model.predict(x_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    matrix = confusion_matrix(y_test, y_pred, labels=sorted(y_test.unique()))

    print("Evaluacion del modelo")
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification report:\n")
    print(report)
    print("Confusion matrix (filas=real, columnas=pred):")
    print(matrix)


if __name__ == "__main__":
    main()
