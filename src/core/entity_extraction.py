"""
Extracción de entidades usando spaCy y dateparser.

- Personas, lugares, organizaciones: spaCy
- Fechas y horas: dateparser + regex

Ejemplo de uso:

    from core.entity_extraction import extract_entities
    text = "Recordame el 10 de diciembre a las 18:00 con Juan Pérez en Madrid."
    entities = extract_entities(text)
    print(entities)
    # [{'text': 'Juan Pérez', 'label': 'PER'}, {'text': 'Madrid', 'label': 'LOC'}, {'text': '10 de diciembre', 'label': 'DATE', 'value': ...}, ...]
"""
import spacy
from typing import List, Dict
import dateparser
import re

# Cargar modelo spaCy español
nlp = spacy.load("es_core_news_sm")

DATE_REGEX = r"\b(\d{1,2} de [a-zA-Z]+( de \d{4})?|hoy|mañana|pasado mañana|ayer|anoche|esta noche|esta tarde|esta mañana)\b"
TIME_REGEX = r"\b(\d{1,2}(:\d{2})? ?(am|pm)?|mediodía|medianoche)\b"

def extract_entities(text: str) -> List[Dict]:
    """Extrae entidades nombradas y fechas/horas del texto."""
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    # Extraer fechas
    for match in re.finditer(DATE_REGEX, text, re.IGNORECASE):
        date_str = match.group(0)
        dt = dateparser.parse(date_str, languages=["es"])
        if dt:
            entities.append({"text": date_str, "label": "DATE", "value": dt.isoformat()})
    # Extraer horas
    for match in re.finditer(TIME_REGEX, text, re.IGNORECASE):
        time_str = match.group(0)
        dt = dateparser.parse(time_str, languages=["es"])
        if dt:
            entities.append({"text": time_str, "label": "TIME", "value": dt.isoformat()})
    return entities
