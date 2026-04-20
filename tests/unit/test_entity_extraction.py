def test_negacion_y_pregunta():
    casos = [
        ("No apagues la luz", True, False, ["apagues", "luz"]),
        ("¿Puedes encender la luz?", False, True, ["encender", "luz"]),
        ("No pongas música y sube el volumen", True, False, ["pongas", "música", "sube", "volumen"]),
        ("¿Quieres que apague la tele?", False, True, ["apague", "tele"]),
        ("Enciende la luz", False, False, ["Enciende", "luz"]),
        ("Jamás abras la puerta", True, False, ["abras", "puerta"]),
        ("¿Puedo abrir la ventana?", False, True, ["abrir", "ventana"]),
    ]
    for texto, neg, preg, entidades_esperadas in casos:
        resultados = extract_entities(texto)
        # Si hay varias frases, al menos una debe cumplir la condición
        assert any(r["negacion"] == neg for r in resultados), f"Negación falló en: {texto}"
        assert any(r["pregunta"] == preg for r in resultados), f"Pregunta falló en: {texto}"
        # Chequear que al menos una frase contenga todas las entidades esperadas
        entidades_detectadas = [e["text"].lower() for r in resultados for e in r["entidades"]]
        for ent in entidades_esperadas:
            assert any(ent.lower() in ed for ed in entidades_detectadas), f"Falta entidad '{ent}' en: {texto}"

import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from core.entity_extraction import segmentar_frases, extract_entities

def test_segmentar_frases_basico():
    texto = "Enciende la luz y apaga la tele. Después pon música; luego sube el volumen"
    esperado = [
        "Enciende la luz",
        "apaga la tele",
        "pon música",
        "sube el volumen"
    ]
    resultado = segmentar_frases(texto)
    assert resultado == esperado, f"Esperado: {esperado}\nObtenido: {resultado}"

def test_extract_entities_frases_compuestas():
    texto = "Enciende la luz y apaga la tele. Después pon música; luego sube el volumen"
    resultados = extract_entities(texto)
    entidades = [e for r in resultados for e in r["entidades"]]
    # Debe detectar al menos un COMANDO y un DISPOSITIVO por frase
    assert any(e["label"] == "COMANDO" and "enciende" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "DISPOSITIVO" and "luz" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "COMANDO" and "apaga" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "DISPOSITIVO" and "tele" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "COMANDO" and "pon" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "DISPOSITIVO" and "musica" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "COMANDO" and "sube" in e["text"].lower() for e in entidades)
    assert any(e["label"] == "DISPOSITIVO" and "volumen" in e["text"].lower() for e in entidades)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from core.entity_extraction import extract_entities

def test_desambiguacion_contextual():
    casos = [
        ("Activa el modo ventilador", [
            {"text": "ventilador", "label": "MODO"}
        ]),
        ("Cierra la puerta principal", [
            {"text": "puerta", "label": "DISPOSITIVO"}
        ]),
        ("Pon la luz en azul", [
            {"text": "luz", "label": "DISPOSITIVO"}, {"text": "azul", "label": "COLOR"}
        ]),
        ("Sube el volumen", [
            {"text": "volumen", "label": "DISPOSITIVO"}
        ]),
        ("Pon la alarma", [
            {"text": "alarma", "label": "DISPOSITIVO"}
        ]),
        ("Activa el modo televisor", [
            {"text": "modo", "label": "MODO"}, {"text": "televisor", "label": "MODO"}
        ]),
    ]
    for frase, esperado in casos:
        resultados = extract_entities(frase)
        entidades = [e for r in resultados for e in r["entidades"]]
        resultado = [{k: e[k] for k in ("text", "label")} for e in entidades]
        for entidad_esperada in esperado:
            assert entidad_esperada in resultado, (
                f"Fallo en: {frase}\nFalta entidad: {entidad_esperada}\nObtenido: {resultado}")
def test_sinonimia_comando():
    frases = [
        ("Enciende la luz", "prende"),
        ("Prendé la lámpara", "prende"),
        ("Actívalo", "prende"),
        ("Apaga la tele", "apaga"),
        ("Desactívalo", "apaga"),
        ("Aumenta el volumen", "sube"),
        ("Disminuye el volumen", "baja"),
        ("Cierra la puerta", "cierra"),
        ("Ábreme la ventana", "abre"),
    ]
    for frase, canonica in frases:
        resultados = extract_entities(frase)
        comandos = [e for r in resultados for e in r["entidades"] if e["label"] == "COMANDO"]
        assert any(e["canonical"] == canonica for e in comandos), f"Fallo en: {frase} -> {comandos}"

def test_sinonimia_dispositivo():
    frases = [
        ("Enciende las luces", "luz"),
        ("Prende la lámpara", "lampara"),
        ("Apaga el televisor", "televisor"),
        ("Pon música", "musica"),
        ("Imprime modelo 3D", "modelo"),
        ("Abre la persiana", "ventana"),
        ("Cierra el portón", "puerta"),
        ("Sube el brillo", "brillo"),
        ("Busca noticias", "noticias"),
        ("Agrega un contacto", "contacto"),
    ]
    for frase, canonica in frases:
        resultados = extract_entities(frase)
        dispositivos = [e for r in resultados for e in r["entidades"] if e["label"] == "DISPOSITIVO"]
        assert any(e["canonical"] == canonica for e in dispositivos), f"Fallo en: {frase} -> {dispositivos}"
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
        resultados = extract_entities(frase)
        entidades = [e for r in resultados for e in r["entidades"]]
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
    resultados = extract_entities(text)
    entities = [e for r in resultados for e in r["entidades"]]
    labels = {e['label'] for e in entities}
    assert 'PER' in labels or 'PERSON' in labels
    assert any('Juan' in e['text'] for e in entities)

def test_extract_entities_location():
    text = "Conectate con Juan Pérez en Madrid."
    resultados = extract_entities(text)
    entities = [e for r in resultados for e in r["entidades"]]
    labels = {e['label'] for e in entities}
    assert 'LOC' in labels
    assert any('Madrid' in e['text'] for e in entities)

def test_extract_entities_date():
    text = "Recordame el 10 de diciembre a las 18:00."
    resultados = extract_entities(text)
    entities = [e for r in resultados for e in r["entidades"]]
    labels = {e['label'] for e in entities}
    assert 'DATE' in labels
    assert any('10 de diciembre' in e['text'] for e in entities)

def test_extract_entities_time():
    text = "La reunión es a las 18:00."
    resultados = extract_entities(text)
    entities = [e for r in resultados for e in r["entidades"]]
    labels = {e['label'] for e in entities}
    assert 'TIME' in labels
    assert any('18:00' in e['text'] for e in entities)

def test_extract_entities_empty():
    text = "Hola, ¿cómo estás?"
    resultados = extract_entities(text)
    # Debe haber al menos una frase segmentada, pero sin entidades
    assert isinstance(resultados, list)
    assert all(len(r["entidades"]) == 0 for r in resultados)
