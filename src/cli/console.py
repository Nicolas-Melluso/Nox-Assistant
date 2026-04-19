"""Simple console CLI to exercise CoreEngine for Fase 0"""
from __future__ import annotations
from typing import Any
from src.core.engine import CoreEngine


def run_console():
    engine = CoreEngine()
    print("NOX CLI (scaffold Fase 0). Escribí 'exit' para salir.")
    while True:
        try:
            text = input('> ')
        except (EOFError, KeyboardInterrupt):
            print('\nSaliendo.')
            break
        if not text:
            continue
        if text.strip().lower() in ('exit', 'quit'):
            print('Saliendo.')
            break
        intent = engine.predict_intent(text)
        print(f"Intent: {intent['intent']} (conf={intent['confidence']})")
