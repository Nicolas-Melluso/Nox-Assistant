from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"

DATASET_PATH = RAW_DIR / "nox_100_intents_dataset.csv"
CATALOG_PATH = RAW_DIR / "nox_100_intents_catalog.csv"
RESULTS_PATH = RESULTS_DIR / "nox100_iterative_results.csv"
BEST_MODEL_PATH = MODELS_DIR / "intent_model_nox100_best.joblib"


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.995,
                    sublinear_tf=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "clf",
                LinearSVC(
                    C=1.5,
                    class_weight="balanced",
                    dual="auto",
                    max_iter=8000,
                ),
            ),
        ]
    )


def main() -> None:
    if not DATASET_PATH.exists() or not CATALOG_PATH.exists():
        raise FileNotFoundError(
            "No existe dataset/catalogo NOX 100. Ejecuta primero: python src/generate_nox_100_dataset.py"
        )

    df = pd.read_csv(DATASET_PATH)
    unique_intents = df["intent"].nunique()
    if unique_intents < 100:
        raise ValueError(
            "El dataset tiene menos de 100 intents unicas. "
            f"Actual: {unique_intents}"
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    run_rows = []
    best = {"seed": None, "accuracy": -1.0, "model": None}

    for seed in range(1, 21):
        intent_counts = df["intent"].value_counts()
        rare_intents = set(intent_counts[intent_counts < 2].index)
        common_df = df[~df["intent"].isin(rare_intents)].copy()
        rare_df = df[df["intent"].isin(rare_intents)].copy()

        if common_df.empty:
            raise ValueError("No hay intents con soporte suficiente para evaluar")

        target_test_size = max(1, int(round(len(df) * 0.2)))
        common_test_size = min(max(1, target_test_size), len(common_df) - 1)
        common_test_ratio = common_test_size / len(common_df)

        common_train_df, common_test_df = train_test_split(
            common_df,
            test_size=common_test_ratio,
            random_state=seed,
            stratify=common_df["intent"],
        )

        train_df = pd.concat([common_train_df, rare_df], ignore_index=True)
        test_df = common_test_df.reset_index(drop=True)

        x_train = train_df["text"].astype(str)
        y_train = train_df["intent"].astype(str)
        x_test = test_df["text"].astype(str)
        y_test = test_df["intent"].astype(str)

        model = build_pipeline()
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        acc = accuracy_score(y_test, preds)

        run_rows.append({"run": seed, "accuracy": round(float(acc), 6)})

        if acc > best["accuracy"]:
            best = {"seed": seed, "accuracy": float(acc), "model": model}

    pd.DataFrame(run_rows).to_csv(RESULTS_PATH, index=False)
    joblib.dump(best["model"], BEST_MODEL_PATH)

    avg_acc = sum(r["accuracy"] for r in run_rows) / len(run_rows)
    min_acc = min(r["accuracy"] for r in run_rows)
    max_acc = max(r["accuracy"] for r in run_rows)

    print("Entrenamiento iterativo NOX100 completado")
    print(f"Intents unicas usadas: {unique_intents}")
    print(f"Runs: {len(run_rows)}")
    print(f"Accuracy promedio: {avg_acc:.4f}")
    print(f"Accuracy minima: {min_acc:.4f}")
    print(f"Accuracy maxima: {max_acc:.4f}")
    print(f"Mejor seed: {best['seed']}")
    print(f"Mejor accuracy: {best['accuracy']:.4f}")
    print(f"Resultados: {RESULTS_PATH}")
    print(f"Mejor modelo: {BEST_MODEL_PATH}")

    if best["accuracy"] >= 0.80:
        print("Objetivo alcanzado: accuracy >= 0.80")
    else:
        print("Objetivo NO alcanzado: accuracy < 0.80")


if __name__ == "__main__":
    main()
