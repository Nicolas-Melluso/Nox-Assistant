import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from model import get_model_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = PROJECT_ROOT / "data" / "train_test" / "test.csv"


def evaluate_model(version: str = "v1") -> dict[str, object]:
    if not TEST_PATH.exists():
        raise FileNotFoundError("No existe test.csv. Ejecuta primero: python src/data_pipeline.py")

    model_path = get_model_path(version)
    if not model_path.exists():
        raise FileNotFoundError("No existe el modelo. Ejecuta primero: python src/model.py")

    test_df = pd.read_csv(TEST_PATH)
    x_test = test_df["text"].astype(str)
    y_test = test_df["intent"].astype(str)

    model = joblib.load(model_path)
    y_pred = model.predict(x_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    matrix = confusion_matrix(y_test, y_pred, labels=sorted(y_test.unique()))

    return {
        "accuracy": acc,
        "report": report,
        "matrix": matrix,
        "model_path": model_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evalua el clasificador de intenciones")
    parser.add_argument("--version", default="v1", help="Version del modelo: v1 o v2")
    args = parser.parse_args()

    result = evaluate_model(version=args.version)

    print("Evaluacion del modelo")
    print(f"Version del modelo: {args.version}")
    print(f"Modelo cargado desde: {result['model_path']}")
    print(f"Accuracy: {result['accuracy']:.4f}")
    print("\nClassification report:\n")
    print(result["report"])
    print("Confusion matrix (filas=real, columnas=pred):")
    print(result["matrix"])


if __name__ == "__main__":
    main()
