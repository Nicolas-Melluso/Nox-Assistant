import argparse

from data_pipeline import run_data_pipeline
from evaluate import evaluate_model
from model import train_model
from predict import predict_intent


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta Fase 1 completa del proyecto")
    parser.add_argument("--version", default="v1", help="Version del modelo: v1, v2 o v3")
    parser.add_argument(
        "--predict-text",
        default="enciende las luces del patio",
        help="Texto de prueba para la prediccion final",
    )
    args = parser.parse_args()

    pipeline_result = run_data_pipeline()
    model_path = train_model(version=args.version)
    evaluation_result = evaluate_model(version=args.version)
    prediction = predict_intent(args.predict_text, version=args.version)

    print("Fase 1 completada")
    print(f"Version ejecutada: {args.version}")
    print(
        "Dataset: "
        f"{pipeline_result['total_examples']} ejemplos, "
        f"{pipeline_result['unique_intents']} intenciones"
    )
    print(f"Modelo generado: {model_path}")
    print(f"Accuracy: {evaluation_result['accuracy']:.4f}")
    print(f"Prediccion de prueba: {args.predict_text} -> {prediction}")


if __name__ == "__main__":
    main()