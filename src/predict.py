from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "intent_model.joblib"


def predict_intent(text: str) -> str:
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Modelo no encontrado. Ejecuta primero: python src/model.py")

    model = joblib.load(MODEL_PATH)
    pred = model.predict([text])[0]
    return pred


def main() -> None:
    examples = [
        "enciende las luces del patio",
        "pon musica relajante",
        "que hora es ahora",
        "apaga la television",
        "pon una alarma para las 6 am",
    ]

    print("Predicciones de ejemplo")
    for text in examples:
        intent = predict_intent(text)
        print(f"- Texto: {text} -> Intent: {intent}")


if __name__ == "__main__":
    main()
