from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning_loop import append_signals_to_feedback, extract_signals


def main() -> None:
    parser = argparse.ArgumentParser(description="NOX continuous training signal collector")
    parser.add_argument("--max-items", type=int, default=400, help="Max lines to inspect in logs")
    args = parser.parse_args()

    signals = extract_signals(max_items=max(50, args.max_items))
    result = append_signals_to_feedback(signals)

    print("NOX learning loop")
    print(f"- signals extraidas: {result['total_signals']}")
    print(f"- filas agregadas a feedback: {result['added']}")
    print(f"- archivo: {result['feedback_file']}")
    print("Siguiente paso: revisa nox_feedback.csv y luego ejecuta apply_feedback.py + train_nox250_iterative.py")


if __name__ == "__main__":
    main()
