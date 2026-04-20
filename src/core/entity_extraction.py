"""
Extracción de entidades usando spaCy y dateparser.

- Personas, lugares, organizaciones: spaCy
- Fechas y horas: dateparser + regex

Ejemplo de uso:

    text = "Recordame el 10 de diciembre a las 18:00 con Juan Pérez en Madrid."
    entities = extract_entities(text)
    print(entities)
    # [{'text': 'Juan Pérez', 'label': 'PER'}, {'text': 'Madrid', 'label': 'LOC'}, {'text': '10 de diciembre', 'label': 'DATE', 'value': ...}, ...]
"""
import spacy
from spacy.pipeline import EntityRuler
from typing import List, Dict
import dateparser
import re

# Cargar modelo spaCy español
nlp = spacy.load("es_core_news_sm")

# --- EntityRuler: patrones personalizados ---
from .entity_patterns import patterns
# Agregar EntityRuler usando la API moderna de spaCy y configurando phrase_matcher_attr para permitir match por LOWER
if "entity_ruler" not in nlp.pipe_names:
    nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
ruler = nlp.get_pipe("entity_ruler")
ruler.add_patterns(patterns)

DATE_REGEX = r"\b(\d{1,2} de [a-zA-Z]+( de \d{4})?|hoy|mañana|pasado mañana|ayer|anoche|esta noche|esta tarde|esta mañana)\b"
TIME_REGEX = r"\b(\d{1,2}(:\d{2})? ?(am|pm)?|mediodía|medianoche)\b"

def extract_entities(text: str) -> List[Dict]:
    """Extrae entidades nombradas y fechas/horas del texto."""
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # --- Post-procesamiento para DISPOSITIVO ---
    # Lista de dispositivos desde los patrones
    from .entity_patterns import patterns
    dispositivo_terms = set()
    for p in patterns:
        if p.get("label") == "DISPOSITIVO":
            # Si el patrón es string
            if isinstance(p["pattern"], str):
                dispositivo_terms.add(p["pattern"].lower())
            # Si el patrón es lista de tokens
            elif isinstance(p["pattern"], list):
                # Solo agregamos si es un solo token
                if len(p["pattern"]) == 1 and "LOWER" in p["pattern"][0]:
                    dispositivo_terms.add(p["pattern"][0]["LOWER"].lower())
    # Buscar dispositivos en el texto
    tokens_lower = [t.text.lower() for t in doc]
    for i, token in enumerate(tokens_lower):
        if token in dispositivo_terms:
            # Evitar duplicados
            if not any(e["text"].lower() == token and e["label"] == "DISPOSITIVO" for e in entities):
                entities.append({"text": doc[i].text, "label": "DISPOSITIVO"})

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
