# Este archivo fue renombrado para evitar que pytest lo recoja como test unitario.
# Uso: python z/entity_extraction_interactive_script.py

import sys, os
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

try:
    from core.entity_extraction import extract_entities, segmentar_frases
except ImportError:
    # Fallback para ejecución desde raíz del repo
    try:
        from src.core.entity_extraction import extract_entities, segmentar_frases
    except ImportError as e:
        print("No se pudo importar extract_entities ni segmentar_frases. Asegúrate de ejecutar desde la carpeta custom-voice-assistant o de tener PYTHONPATH configurado.")
        raise e

print("Modo interactivo: escribe una frase y presiona Enter (escribe 'salir' para terminar)")
while True:
    texto = input("Frase: ")
    if texto.strip().lower() == "salir":
        print("Saliendo...")
        break
    resultados = extract_entities(texto)
    print(f"Frases segmentadas ({len(resultados)}):")
    for i, res in enumerate(resultados, 1):
        print(f"  {i}. {res['frase']}")
        print(f"    Negación: {res['negacion']} | Pregunta: {res['pregunta']}")
        print(f"    Entidades: {res['entidades']}")
    print("-" * 40)
