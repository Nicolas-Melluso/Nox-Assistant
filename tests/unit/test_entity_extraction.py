def test_entity_extraction_accuracy():
    casos = [
        ("Enciende las luces", ["DISPOSITIVO", "COMANDO"]),
        ("Apaga la tele", ["DISPOSITIVO", "COMANDO"]),
        ("Sube el volumen", ["DISPOSITIVO", "COMANDO"]),
        ("Abre la puerta", ["DISPOSITIVO", "COMANDO"]),
        ("Pon música", ["DISPOSITIVO", "COMANDO"]),
        ("Imprime modelo 3D", ["DISPOSITIVO", "COMANDO"]),
        ("Llama a Juan Pérez", ["COMANDO", "PER"]),
        ("Qué clima hace", ["DISPOSITIVO", "COMANDO"]),
        ("Busca noticias", ["DISPOSITIVO", "COMANDO"]),
        ("Crea nota", ["DISPOSITIVO", "COMANDO"]),
        ("Activa modo interrumpir", ["COMANDO"]),
        ("Haz chequeo médico", ["COMANDO"]),
        ("Pon alarma", ["COMANDO"]),
    ]
    total = 0
    correct = 0
    for frase, esperados in casos:
        entidades = extract_entities(frase)
        print(f"Frase: {frase}")
        print("Entidades detectadas:", entidades)
        labels = [e["label"] for e in entidades]
        for esperado in esperados:
            total += 1
            if esperado in labels:
                correct += 1
    accuracy = correct / total if total > 0 else 0
    print(f"Accuracy extracción entidades: {accuracy:.2%}")
    assert accuracy > 0.8  # Esperamos al menos 80% de acierto
import pytest
from core.entity_extraction import extract_entities

def test_extract_entities_person():
    text = "Conectate con Juan Pérez en Madrid."
    entities = extract_entities(text)
    labels = {e['label'] for e in entities}
    assert 'PER' in labels or 'PERSON' in labels
    assert any('Juan' in e['text'] for e in entities)

def test_extract_entities_location():
    text = "Conectate con Juan Pérez en Madrid."
    entities = extract_entities(text)
    labels = {e['label'] for e in entities}
    assert 'LOC' in labels
    assert any('Madrid' in e['text'] for e in entities)

def test_extract_entities_date():
    text = "Recordame el 10 de diciembre a las 18:00."
    entities = extract_entities(text)
    labels = {e['label'] for e in entities}
    assert 'DATE' in labels
    assert any('10 de diciembre' in e['text'] for e in entities)

def test_extract_entities_time():
    text = "La reunión es a las 18:00."
    entities = extract_entities(text)
    labels = {e['label'] for e in entities}
    assert 'TIME' in labels
    assert any('18:00' in e['text'] for e in entities)

def test_extract_entities_empty():
    text = "Hola, ¿cómo estás?"
    entities = extract_entities(text)
    assert isinstance(entities, list)
    assert len(entities) == 0
