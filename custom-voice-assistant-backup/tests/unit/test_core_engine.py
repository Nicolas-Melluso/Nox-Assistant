from src.core.engine import CoreEngine


def test_predict_intent():
    e = CoreEngine()
    r = e.predict_intent('Hola')
    assert 'intent' in r
    assert 'confidence' in r


def test_execute_skill():
    e = CoreEngine()
    r = e.execute_skill({'intent': 'noop'})
    assert r.get('success') is True
