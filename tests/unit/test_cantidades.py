import pytest
import sys
import os
# Asegura que la raíz de custom-voice-assistant esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core.entity_pipeline.cantidades import extraer_cantidades

@pytest.mark.parametrize("texto, esperado", [
    ("media taza de leche", [{"cantidad": 0.5, "unidad": "taza"}]),
    ("un cuarto de kilo de pan", [{"cantidad": 0.25, "unidad": "kilo"}]),
    ("tres cuartos de litro", [{"cantidad": 0.75, "unidad": "litro"}]),
    ("dos kilos de manzanas", [{"cantidad": 2, "unidad": "kilos"}]),
    ("1/2 litro de agua", [{"cantidad": 0.5, "unidad": "litro"}]),
    ("cien gramos de queso", [{"cantidad": 100, "unidad": "gramos"}]),
    ("una docena de huevos", [{"cantidad": 12, "unidad": "docena"}]),
    ("3 litros de jugo", [{"cantidad": 3, "unidad": "litros"}]),
    ("250 ml de aceite", [{"cantidad": 250, "unidad": "ml"}]),
    ("un octavo de taza", [{"cantidad": 0.125, "unidad": "taza"}]),
    ("dos tercios de litro", [{"cantidad": 2/3, "unidad": "litro"}]),
    ("un medio kilo", [{"cantidad": 0.5, "unidad": "kilo"}]),
])
def test_extraer_cantidades(texto, esperado):
    resultado = extraer_cantidades(texto)
    assert len(resultado) == len(esperado)
    for r, e in zip(resultado, esperado):
        assert abs(r["cantidad"] - e["cantidad"]) < 0.001
        assert r["unidad"].startswith(e["unidad"])  # permite plural/singular
