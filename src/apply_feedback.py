import argparse
from pathlib import Path

import pandas as pd

from data_pipeline import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "intent_dataset.csv"
DEFAULT_FEEDBACK_PATH = PROJECT_ROOT / "data" / "raw" / "nox_feedback.csv"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Incorpora feedback de NOX al dataset base para reentrenar"
    )
    parser.add_argument(
        "--feedback-file",
        default=str(DEFAULT_FEEDBACK_PATH),
        help="Archivo CSV con columnas text,predicted_intent,correct_intent",
    )
    parser.add_argument(
        "--clear-feedback",
        action="store_true",
        help="Limpia el archivo de feedback luego de incorporarlo",
    )
    args = parser.parse_args()

    feedback_path = Path(args.feedback_file)
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"No existe dataset base: {RAW_DATA_PATH}")

    if not feedback_path.exists():
        print(f"No hay feedback para aplicar en: {feedback_path}")
        return

    raw_df = pd.read_csv(RAW_DATA_PATH)
    feedback_df = pd.read_csv(feedback_path)

    required_feedback_cols = {"text", "predicted_intent", "correct_intent"}
    if not required_feedback_cols.issubset(set(feedback_df.columns)):
        raise ValueError(
            "El feedback CSV debe tener columnas: text,predicted_intent,correct_intent"
        )

    new_samples = feedback_df[["text", "correct_intent"]].copy()
    new_samples = new_samples.rename(columns={"correct_intent": "intent"})
    new_samples["text"] = new_samples["text"].astype(str).map(clean_text)
    new_samples["intent"] = new_samples["intent"].astype(str).str.strip()
    new_samples = new_samples.dropna().drop_duplicates().reset_index(drop=True)

    before_count = len(raw_df)
    merged_df = pd.concat([raw_df, new_samples], ignore_index=True)
    merged_df = merged_df.dropna().drop_duplicates(subset=["text", "intent"]).reset_index(
        drop=True
    )
    added_count = len(merged_df) - before_count

    merged_df.to_csv(RAW_DATA_PATH, index=False)

    print(f"Feedback leido: {len(feedback_df)} filas")
    print(f"Nuevas muestras agregadas al dataset: {added_count}")
    print(f"Dataset actualizado: {RAW_DATA_PATH}")

    if args.clear_feedback:
        feedback_df.head(0).to_csv(feedback_path, index=False)
        print(f"Feedback limpiado: {feedback_path}")


if __name__ == "__main__":
    main()
