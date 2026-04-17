import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = PROJECT_ROOT / "data" / "train_test" / "train.csv"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "intent_model.joblib"


def get_model_path(version: str) -> Path:
    if version == "v1":
        return MODEL_PATH
    return MODELS_DIR / f"intent_model_{version}.joblib"


def build_pipeline(version: str) -> Pipeline:
    if version == "v2":
        return Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 3),
                        min_df=1,
                        max_df=0.98,
                        sublinear_tf=True,
                    ),
                ),
                (
                    "clf",
                    LinearSVC(
                        C=1.0,
                        dual="auto",
                        max_iter=5000,
                    ),
                ),
            ]
        )

    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=200,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def train_model(version: str = "v1") -> Path:
    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            "No existe train.csv. Ejecuta primero: python src/data_pipeline.py"
        )

    train_df = pd.read_csv(TRAIN_PATH)
    x_train = train_df["text"].astype(str)
    y_train = train_df["intent"].astype(str)

    pipeline = build_pipeline(version)

    pipeline.fit(x_train, y_train)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = get_model_path(version)
    joblib.dump(pipeline, model_path)

    return model_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena el clasificador de intenciones")
    parser.add_argument("--version", default="v1", help="Version del modelo: v1 o v2")
    args = parser.parse_args()

    model_path = train_model(version=args.version)

    print("Entrenamiento completado")
    print(f"Version del modelo: {args.version}")
    print(f"Modelo guardado en: {model_path}")


if __name__ == "__main__":
    main()
