import re
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "intent_dataset.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TRAIN_TEST_DIR = PROJECT_ROOT / "data" / "train_test"


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9áéíóúñü\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def run_data_pipeline() -> dict[str, object]:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"No se encontro el dataset en: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)

    required_cols = {"text", "intent"}
    if set(df.columns) != required_cols:
        raise ValueError("El CSV debe tener columnas exactas: text,intent")

    df["text"] = df["text"].astype(str).map(clean_text)
    df["intent"] = df["intent"].astype(str).str.strip()
    df = df.dropna().drop_duplicates().reset_index(drop=True)

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["intent"],
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TRAIN_TEST_DIR.mkdir(parents=True, exist_ok=True)

    processed_path = PROCESSED_DIR / "intent_dataset_clean.csv"
    train_path = TRAIN_TEST_DIR / "train.csv"
    test_path = TRAIN_TEST_DIR / "test.csv"

    df.to_csv(processed_path, index=False)
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    return {
        "total_examples": len(df),
        "train_examples": len(train_df),
        "test_examples": len(test_df),
        "unique_intents": df["intent"].nunique(),
        "processed_path": processed_path,
        "train_path": train_path,
        "test_path": test_path,
    }


def main() -> None:
    result = run_data_pipeline()

    print("Pipeline de datos completado")
    print(f"Total ejemplos: {result['total_examples']}")
    print(f"Train: {result['train_examples']} | Test: {result['test_examples']}")
    print(f"Intentos unicos: {result['unique_intents']}")
    print(f"Archivo limpio: {result['processed_path']}")
    print(f"Train: {result['train_path']}")
    print(f"Test: {result['test_path']}")


if __name__ == "__main__":
    main()
