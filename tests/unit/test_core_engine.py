import pytest


def test_predict_intent(engine):
    r = engine.predict_intent('Conectate con Juan Pérez en Madrid el 5 de mayo.')
    assert 'intent' in r
    assert 'confidence' in r
    assert 'entities' in r
    assert isinstance(r['entities'], list)
    # Debe detectar al menos una entidad
    # r['entities'] es ahora una lista de frases, cada una con 'entidades'
    entidades = [e for frase in r['entities'] for e in frase.get('entidades', [])]
    assert any(e['label'] in ['PER', 'PERSON', 'LOC', 'DATE'] for e in entidades)

def test_execute_skill(engine):
    r = engine.execute_skill({'intent': 'noop'})
    assert r.get('success') is True
