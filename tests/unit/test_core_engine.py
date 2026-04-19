import pytest

def test_predict_intent(engine):
    r = engine.predict_intent('Hola')
    assert 'intent' in r
    assert 'confidence' in r

def test_execute_skill(engine):
    r = engine.execute_skill({'intent': 'noop'})
    assert r.get('success') is True
