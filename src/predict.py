import argparse
from pathlib import Path

import joblib

from model import get_model_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "intent_model.joblib"


def predict_intent(text: str, version: str = "v1") -> str:
    model_path = get_model_path(version)
    if not model_path.exists():
        raise FileNotFoundError("Modelo no encontrado. Ejecuta primero: python src/model.py")

    model = joblib.load(model_path)
    pred = model.predict([text])[0]
    return pred


def main() -> None:
    parser = argparse.ArgumentParser(description="Predice la intencion de uno o varios textos")
    parser.add_argument(
        "--version",
        default="v1",
        help="Version del modelo: v1, v2, v3 o alias nox/nox100/best",
    )
    parser.add_argument("--text", help="Texto unico a clasificar")
    args = parser.parse_args()

    examples = [
        "enciende las luces del patio",
        "pon musica relajante",
        "que hora es ahora",
        "apaga la television",
        "pon una alarma para las 6 am",
    ]

    if args.text:
        examples = [args.text]

    print("Predicciones de ejemplo")
    for text in examples:
        intent = predict_intent(text, version=args.version)
        print(f"- Texto: {text} -> Intent: {intent}")


if __name__ == "__main__":
    main()
