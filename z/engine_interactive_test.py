"""
Script interactivo para probar CoreEngine y predict_intent (0.3.5)
Robusto: permite ejecución desde cualquier carpeta (local o Docker).
"""
import sys
import os

# Agrega la raíz del proyecto al sys.path si no está
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.core.engine import CoreEngine

if __name__ == "__main__":
    engine = CoreEngine()
    print("Prueba interactiva de CoreEngine (0.3.5)")
    print("Escribe una frase (Ctrl+C para salir):")
    while True:
        try:
            text = input("> ")
            result = engine.predict_intent(text)
            print("\nResultado:")
            print(result)
            print()
        except KeyboardInterrupt:
            print("\nSaliendo.")
            break
