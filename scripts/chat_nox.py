import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import argparse
import csv

from action_executor import RISKY_INTENTS, execute_action
from entity_extractor import extract_entities
from intent_router import route_intent
from model import get_model_path
from predict import predict_intent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "intent_dataset.csv"
NOX100_CATALOG_PATH = PROJECT_ROOT / "data" / "raw" / "nox_100_intents_catalog.csv"
NOX250_CATALOG_PATH = PROJECT_ROOT / "data" / "raw" / "nox_250_intents_catalog.csv"
DEFAULT_FEEDBACK_PATH = PROJECT_ROOT / "data" / "raw" / "nox_feedback.csv"


def load_known_intents(version: str) -> list[str]:
    intents: set[str] = set()
    source_path = RAW_DATA_PATH
    source_intent_field = "intent"

    if version in {"nox", "nox250", "best"} and NOX250_CATALOG_PATH.exists():
        source_path = NOX250_CATALOG_PATH
    elif version in {"nox100"} and NOX100_CATALOG_PATH.exists():
        source_path = NOX100_CATALOG_PATH

    with source_path.open("r", encoding="utf-8", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            intent = (row.get(source_intent_field) or "").strip()
            target_intent = (row.get("target_intent") or "").strip()
            if intent:
                intents.add(intent)
            if target_intent:
                intents.add(target_intent)
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
    parser.add_argument(
        "--version",
        default="nox250",
        help="Version del modelo: v1, v2, v3 o alias nox/nox100/nox250/best",
    )
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
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Desactiva la ejecucion real de acciones (modo prueba)",
    )
    args = parser.parse_args()
    feedback_path = Path(args.feedback_file)
    known_intents = set(load_known_intents(args.version))
    model_path = get_model_path(args.version)

    print("NOX Assistant - modo interactivo")
    print(f"Modelo activo: {args.version}")
    print(f"Archivo de modelo: {model_path}")
    if args.no_feedback:
        print("Captura de feedback: desactivada")
    else:
        print(f"Captura de feedback: activada -> {feedback_path}")
    if args.no_execute:
        print("Ejecucion de acciones: desactivada (modo prueba)")
    else:
        print("Ejecucion de acciones: activada")
    print("Escribe un comando. Usa 'salir' para terminar.")

    while True:
        user_text = input("> ").strip()
        if not user_text:
            continue

        if user_text.lower() in {"salir", "exit", "quit"}:
            print("Cerrando NOX.")
            break

        predicted_intent = predict_intent(user_text, version=args.version)
        intent, routing_reason = route_intent(user_text, predicted_intent)
        if routing_reason:
            print(f"Intent corregida: {predicted_intent} -> {intent}")
            print(f"Motivo: {routing_reason}")
        entities = extract_entities(user_text, intent)
        if entities:
            entity_str = "  ".join(f"{k}={v}" for k, v in entities.items())
            print(f"Intent: {intent}  |  Entidades: {entity_str}")
        else:
            print(f"Intent: {intent}")

        if not args.no_execute:
            result = execute_action(intent, entities)
            status = result["status"]

            if status == "confirm_required":
                confirm = input(f"  [!] {result['message']} [s/n]: ").strip().lower()
                if confirm in {"s", "si", "sí", "y", "yes"}:
                    result = execute_action(intent, entities, force=True)
                    print(f"  -> {result['message']}")
                else:
                    print("  Accion cancelada.")
            elif status == "ok":
                print(f"  -> {result['message']}")
            elif status == "not_implemented":
                print(f"  [~] {result['message']}")
            elif status == "error":
                print(f"  [x] {result['message']}")

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