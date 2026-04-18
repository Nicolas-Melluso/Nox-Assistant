import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import argparse

import pandas as pd

from data_pipeline import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "intent_dataset.csv"
NOX100_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "nox_100_intents_dataset.csv"
NOX100_CATALOG_PATH = PROJECT_ROOT / "data" / "raw" / "nox_100_intents_catalog.csv"
NOX250_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "nox_250_intents_dataset.csv"
NOX250_CATALOG_PATH = PROJECT_ROOT / "data" / "raw" / "nox_250_intents_catalog.csv"
DEFAULT_FEEDBACK_PATH = PROJECT_ROOT / "data" / "raw" / "nox_feedback.csv"


def get_target_paths(target: str) -> tuple[Path, Path | None]:
    if target == "nox250":
        return NOX250_DATA_PATH, NOX250_CATALOG_PATH
    if target == "nox100":
        return NOX100_DATA_PATH, NOX100_CATALOG_PATH
    return RAW_DATA_PATH, None


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
        "--target",
        choices=["base", "nox100", "nox250"],
        default="base",
        help="Dataset objetivo para aplicar feedback",
    )
    parser.add_argument(
        "--clear-feedback",
        action="store_true",
        help="Limpia el archivo de feedback luego de incorporarlo",
    )
    args = parser.parse_args()

    target_data_path, target_catalog_path = get_target_paths(args.target)

    feedback_path = Path(args.feedback_file)
    if not target_data_path.exists():
        raise FileNotFoundError(f"No existe dataset objetivo: {target_data_path}")

    if not feedback_path.exists():
        print(f"No hay feedback para aplicar en: {feedback_path}")
        return

    raw_df = pd.read_csv(target_data_path)
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

    merged_df.to_csv(target_data_path, index=False)

    if target_catalog_path is not None and target_catalog_path.exists():
        catalog_df = pd.read_csv(target_catalog_path)
        catalog_intents = set(catalog_df["intent"].astype(str).str.strip())
        new_intents = sorted(set(new_samples["intent"]) - catalog_intents)
        if new_intents:
            # Usa la primera frase vista como comando canonico provisional.
            extra_rows = []
            for intent in new_intents:
                sample_text = (
                    new_samples[new_samples["intent"] == intent]["text"].iloc[0]
                )
                row = {"intent": intent, "canonical_command": sample_text}
                if "target_intent" in catalog_df.columns:
                    row["target_intent"] = intent
                if "style" in catalog_df.columns:
                    row["style"] = "feedback"
                extra_rows.append(row)
            catalog_df = pd.concat([catalog_df, pd.DataFrame(extra_rows)], ignore_index=True)
            catalog_df = catalog_df.drop_duplicates(subset=["intent"]).reset_index(drop=True)
            catalog_df.to_csv(target_catalog_path, index=False)
            print(
                "Nuevas intents agregadas al catalogo NOX100: "
                f"{', '.join(new_intents)}"
            )

    print(f"Feedback leido: {len(feedback_df)} filas")
    print(f"Nuevas muestras agregadas al dataset: {added_count}")
    print(f"Dataset actualizado: {target_data_path}")

    if args.clear_feedback:
        feedback_df.head(0).to_csv(feedback_path, index=False)
        print(f"Feedback limpiado: {feedback_path}")


if __name__ == "__main__":
    main()
