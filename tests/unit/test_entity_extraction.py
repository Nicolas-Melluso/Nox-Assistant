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
