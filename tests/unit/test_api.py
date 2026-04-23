import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from api.main import app
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

@pytest.mark.parametrize("text,expected_intent", [
    ("Quiero reservar un vuelo a Madrid mañana", "unknown"),
    ("responde a la pregunta", "answer"),
    ("escribe un texto", "write"),
    ("pon la alarma", "set"),
    ("enciende la luz", "turn_on"),
])
def test_predict_intent(text, expected_intent):
    response = client.post("/predict_intent", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert data["intent"] == expected_intent
    assert "score" in data
    assert "entities" in data
    assert "input_text" in data

@pytest.mark.parametrize("text", [
    "Quiero reservar un vuelo a Madrid mañana",
    "escribe un texto",
    "enciende la luz",
])
def test_extract_entities(text):
    response = client.post("/extract_entities", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert isinstance(data["entities"], list)
