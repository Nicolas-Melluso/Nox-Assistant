
# Prueba interactiva para extracción de entidades (NO TEST UNITARIO)

# Importar para ejecución directa o como módulo
try:
    from src.core.entity_extraction import extract_entities
except ModuleNotFoundError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
    from core.entity_extraction import extract_entities


print("Modo interactivo: escribe una frase y presiona Enter (escribe 'salir' para terminar)")
while True:
    frase = input("Frase: ")
    if frase.strip().lower() == "salir":
        print("Saliendo...")
        break
    entidades = extract_entities(frase)
    print("Entidades:", entidades)
    print("-" * 40)
