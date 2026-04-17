from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = PROJECT_ROOT / "data" / "train_test" / "train.csv"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "intent_model.joblib"


def main() -> None:
    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            "No existe train.csv. Ejecuta primero: python src/data_pipeline.py"
        )

    train_df = pd.read_csv(TRAIN_PATH)
    x_train = train_df["text"].astype(str)
    y_train = train_df["intent"].astype(str)

    # Pipeline simple y robusto para clasificacion de intenciones.
    pipeline = Pipeline(
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

    pipeline.fit(x_train, y_train)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    print("Entrenamiento completado")
    print(f"Modelo guardado en: {MODEL_PATH}")


if __name__ == "__main__":
    main()
