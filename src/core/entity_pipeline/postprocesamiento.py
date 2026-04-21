import re
import dateparser
from .regexes import DATE_REGEX, TIME_REGEX
from .nlp_singleton import nlp
from ..entity_patterns import patterns
from ..utils import limpiar_y_normalizar, normalizar_entidad_sinonimos

def postprocesar_entidades(entities, text):
    dispositivo_terms = set()
    for p in patterns:
        if p.get("label") == "DISPOSITIVO":
            if isinstance(p["pattern"], str):
                dispositivo_terms.add(p["pattern"].lower())
            elif isinstance(p["pattern"], list):
                if (
                    len(p["pattern"]) == 1
                    and "LOWER" in p["pattern"][0]
                    and isinstance(p["pattern"][0]["LOWER"], str)
                ):
                    dispositivo_terms.add(p["pattern"][0]["LOWER"].lower())
    texto_limpio = limpiar_y_normalizar(text)
    doc_limpio = nlp(texto_limpio)
    tokens_lower = [t.text.lower() for t in doc_limpio]
    dispositivos_detectados = set(e["text"].lower() for e in entities if e["label"] == "DISPOSITIVO")
    for i, token in enumerate(tokens_lower):
        if token in dispositivo_terms:
            if token not in dispositivos_detectados:
                entities.append({"text": doc_limpio[i].text, "label": "DISPOSITIVO"})
                dispositivos_detectados.add(token)
    hay_comando = any(e["label"] == "COMANDO" for e in entities)
    hay_dispositivo = any(e["label"] == "DISPOSITIVO" for e in entities)
    if hay_comando and not hay_dispositivo:
        texto_busqueda = text.lower()
        for term in sorted(dispositivo_terms, key=len, reverse=True):
            if term in texto_busqueda:
                idx = texto_busqueda.find(term)
                entidad = text[idx:idx+len(term)]
                entities.append({"text": entidad, "label": "DISPOSITIVO"})
                break
    # Fechas
    for match in re.finditer(DATE_REGEX, text, re.IGNORECASE):
        date_str = match.group(0)
        dt = dateparser.parse(date_str, languages=["es"])
        if dt:
            entities.append({"text": date_str, "label": "DATE", "value": dt.isoformat()})
    # Horas
    for match in re.finditer(TIME_REGEX, text, re.IGNORECASE):
        time_str = match.group(0)
        dt = dateparser.parse(time_str, languages=["es"])
        if dt:
            entities.append({"text": time_str, "label": "TIME", "value": dt.isoformat()})
    # Sinonimia
    for ent in entities:
        if ent["label"] in ("COMANDO", "DISPOSITIVO"):
            ent["canonical"] = normalizar_entidad_sinonimos(ent["text"], ent["label"])
    # Volumen
    texto_busqueda = text.lower()
    volumen_detectado = any(e["label"] == "DISPOSITIVO" and e["text"].lower() == "volumen" for e in entities)
    if "volumen" in texto_busqueda and not volumen_detectado:
        idx = texto_busqueda.find("volumen")
        entidad = text[idx:idx+len("volumen")]
        entities.append({"text": entidad, "label": "DISPOSITIVO"})
    return entities
