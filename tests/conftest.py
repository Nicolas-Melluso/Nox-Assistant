import pytest
import sys
import os

# Agregar src/ al sys.path para que los imports funcionen
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.engine import CoreEngine
from core.intent_classifier import MockIntentClassifier
from core.os_control import SubprocessOSController


@pytest.fixture
def engine():
    """Fixture que retorna una instancia de CoreEngine para los tests.

    Por defecto se inyecta un `MockIntentClassifier` y un
    `SubprocessOSController(dry_run=True)` para evitar descargas de modelos
    y efectos sobre el sistema en CI/local.
    """
    # Inyectar extractor de entidades simple para tests (evita cargar spaCy pero
    # retorna una estructura similar a la producción).
    import re

    def simple_entity_extractor(text: str):
        if not text:
            return []
        entidades = []
        seen_spans = set()

        # Fecha simple: '5 de mayo', '12 de enero'
        date_re = re.compile(r"\b\d{1,2}\s+de\s+[A-Za-záéíóúñÑ]+\b", re.I)
        for m in date_re.finditer(text):
            if (m.start(), m.end()) in seen_spans:
                continue
            seen_spans.add((m.start(), m.end()))
            entidades.append({"text": m.group(0), "label": "DATE"})

        # Nombres propios (dos palabras con mayúscula inicial)
        name_re = re.compile(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+\b")
        for m in name_re.finditer(text):
            if (m.start(), m.end()) in seen_spans:
                continue
            seen_spans.add((m.start(), m.end()))
            entidades.append({"text": m.group(0), "label": "PER"})

        # Localidades/ciudades (palabra mayúscula sola)
        city_re = re.compile(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,})\b")
        for m in city_re.finditer(text):
            span = (m.start(), m.end())
            if span in seen_spans:
                continue
            token = m.group(1)
            # Evitar capturar la primera palabra de la frase si no es nombre propio
            if token[0].isupper():
                entidades.append({"text": token, "label": "LOC"})

        return [{"frase": text, "entidades": entidades}]

    return CoreEngine(classifier=MockIntentClassifier(), os_controller=SubprocessOSController(dry_run=True), entity_extractor=simple_entity_extractor)
