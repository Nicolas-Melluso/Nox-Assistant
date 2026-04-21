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


def test_predict_intent_basic():
    from core.engine import CoreEngine
    engine = CoreEngine()
    casos = [
        ("Enciende la luz", "turn_on"),
        ("Apaga la tele", "turn_off"),
        ("Sube el volumen", "increase"),
        ("Baja la música", "decrease"),
        ("Pon la alarma", "set"),
        ("Configura el wifi", "configure"),
        ("Llama a Juan", "call"),
        ("Busca noticias", "search"),
        ("Abre la puerta", "open"),
        ("Cierra la ventana", "close"),
        ("Crea una nota", "create"),
        ("Genera un reporte", "generate"),
        ("Muestra el clima", "show"),
        ("Oculta la barra", "hide"),
        ("Reproduce música", "play"),
        ("Pausa la canción", "pause"),
        ("Detén el temporizador", "stop"),
        ("Responde el mensaje", "answer"),
        ("Escribe un mail", "write"),
        ("Lee el mensaje", "read"),
        ("Elimina el archivo", "delete"),
        ("Borra la nota", "delete"),
        ("Actualiza el sistema", "update"),
        ("Sincroniza contactos", "sync"),
        ("Descarga el archivo", "download"),
        ("Envía un mensaje", "send"),
        ("Manda la ubicación", "send"),
        ("Haz algo desconocido", "unknown"),
    ]
    for frase, intent_esperado in casos:
        result = engine.predict_intent(frase)
        assert result["intent"] == intent_esperado, f"Fallo en: {frase} -> {result['intent']}"
        if intent_esperado != "unknown":
            assert result["confidence"] >= 0.55, f"Confianza baja para: {frase} -> {result['confidence']}"
        else:
            assert result["confidence"] == 0.0
