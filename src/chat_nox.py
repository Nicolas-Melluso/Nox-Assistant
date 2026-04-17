import argparse
import csv
from pathlib import Path

from predict import predict_intent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "intent_dataset.csv"
DEFAULT_FEEDBACK_PATH = PROJECT_ROOT / "data" / "raw" / "nox_feedback.csv"


def load_known_intents() -> list[str]:
    intents: set[str] = set()
    with RAW_DATA_PATH.open("r", encoding="utf-8", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            intent = (row.get("intent") or "").strip()
            if intent:
                intents.add(intent)
    return sorted(intents)


def append_feedback(
    feedback_path: Path,
    text: str,
    predicted_intent: str,
    correct_intent: str,
) -> None:
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = feedback_path.exists()

    with feedback_path.open("a", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=["text", "predicted_intent", "correct_intent"],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "text": text,
                "predicted_intent": predicted_intent,
                "correct_intent": correct_intent,
            }
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Consola interactiva para probar NOX por texto")
    parser.add_argument("--version", default="v3", help="Version del modelo: v1, v2 o v3")
    parser.add_argument(
        "--feedback-file",
        default=str(DEFAULT_FEEDBACK_PATH),
        help="Archivo CSV donde se guardan correcciones de intents",
    )
    parser.add_argument(
        "--no-feedback",
        action="store_true",
        help="Desactiva la captura de correcciones",
    )
    args = parser.parse_args()
    feedback_path = Path(args.feedback_file)
    known_intents = set(load_known_intents())

    print("NOX Assistant - modo interactivo")
    print(f"Modelo activo: {args.version}")
    if args.no_feedback:
        print("Captura de feedback: desactivada")
    else:
        print(f"Captura de feedback: activada -> {feedback_path}")
    print("Escribe un comando. Usa 'salir' para terminar.")

    while True:
        user_text = input("> ").strip()
        if not user_text:
            continue

        if user_text.lower() in {"salir", "exit", "quit"}:
            print("Cerrando NOX.")
            break

        intent = predict_intent(user_text, version=args.version)
        print(f"Intent detectada: {intent}")

        if args.no_feedback:
            continue

        confirmation = input("¿Prediccion correcta? [s/n]: ").strip().lower()
        if confirmation in {"s", "si", "sí", "y", "yes"}:
            continue

        print("Intents disponibles:")
        print(", ".join(sorted(known_intents)))
        print("Si falta una intent, puedes escribir una nueva y se guardara para reentrenar.")

        while True:
            correct_intent = input("Intent correcta: ").strip()
            if not correct_intent:
                print("La intent no puede estar vacia.")
                continue

            if correct_intent in known_intents:
                append_feedback(feedback_path, user_text, intent, correct_intent)
                print("Feedback guardado para reentrenar.")
                break

            create_new = input(
                "Esa intent no existe aun. ¿Quieres crearla? [s/n]: "
            ).strip().lower()
            if create_new in {"s", "si", "sí", "y", "yes"}:
                append_feedback(feedback_path, user_text, intent, correct_intent)
                known_intents.add(correct_intent)
                print("Intent nueva guardada en feedback. Agrega mas ejemplos antes de reentrenar.")
                break

            print("Intent no guardada. Prueba con otra intent.")


if __name__ == "__main__":
    main()