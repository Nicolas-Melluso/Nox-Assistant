"""
Extractor de entidades para NOX.

Dado un texto y el intent clasificado, retorna un dict con las entidades
encontradas. Usa reglas + regex, sin dependencias externas.

Ejemplos:
    extract_entities("pon el volumen al 70", "volume_up")
    → {"value": 70}

    extract_entities("pon un timer de diez minutos", "start_timer")
    → {"duration_seconds": 600}

    extract_entities("alarma a las 7:30", "set_alarm")
    → {"time": "07:30"}

    extract_entities("busca en la web noticias de python", "browser_search_web")
    → {"query": "noticias de python"}

    extract_entities("envia un whatsapp a Juan diciendo llegas tarde", "send_whatsapp_message")
    → {"contact": "Juan", "message": "llegas tarde"}
"""

import re
from typing import Optional

# ── Numeros en espanol → int ─────────────────────────────────────────────────

_WORD_NUM: dict[str, int] = {
    "cero": 0,
    "un": 1, "uno": 1, "una": 1,
    "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9,
    "diez": 10, "once": 11, "doce": 12, "trece": 13,
    "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17,
    "dieciocho": 18, "diecinueve": 19, "veinte": 20,
    "veintiuno": 21, "veintidos": 22, "veintitres": 23,
    "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
    "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50,
    "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90,
    "cien": 100, "ciento": 100,
    "medianoche": 0, "mediodia": 12,
}

# Ordenado de mayor a menor longitud para que el regex prefiera el match mas largo
_WORD_NUM_RE = "|".join(sorted(_WORD_NUM.keys(), key=len, reverse=True))


def _to_num(token: str) -> Optional[int]:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return _WORD_NUM.get(token)


def _first_number(text: str) -> Optional[int]:
    """Primer numero (digito o palabra) encontrado en el texto."""
    m = re.search(r"\b(\d+)\b", text)
    if m:
        return int(m.group(1))
    m = re.search(rf"\b({_WORD_NUM_RE})\b", text, re.IGNORECASE)
    if m:
        return _WORD_NUM.get(m.group(1).lower())
    return None


# ── Extractores individuales ─────────────────────────────────────────────────

def _extract_value(text: str) -> Optional[int]:
    """
    Valor numerico (0-100) en contextos como:
      'al 70', 'a 50%', 'en 80', 'subelo a treinta'
    """
    m = re.search(r"\b(?:al?|en)\s+(\d+)\s*%?", text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    if re.search(r"\b(maximo|maxima|max)\b", text, re.IGNORECASE):
        return 100
    if re.search(r"\b(minimo|minima|min)\b", text, re.IGNORECASE):
        return 0
    if re.search(r"\b(medio|mitad|cincuenta)\b", text, re.IGNORECASE):
        return 50

    return _first_number(text)


def _extract_duration_seconds(text: str) -> Optional[int]:
    """
    Duracion para timers. Acepta horas, minutos y segundos en cualquier
    combinacion, con digitos o palabras.
      'diez minutos' → 600
      'una hora y media' → 5400  (no soporta 'y media' todavia, retorna 3600)
      '2 horas 30 minutos' → 9000
    """
    total = 0
    found = False

    for unit, multiplier in [("hora[s]?", 3600), ("minutos?", 60), ("segundos?", 1)]:
        m = re.search(rf"\b(\d+|{_WORD_NUM_RE})\s+{unit}", text, re.IGNORECASE)
        if m:
            v = _to_num(m.group(1))
            if v is not None:
                total += v * multiplier
                found = True

    return total if found else None


def _extract_time(text: str) -> Optional[str]:
    """
    Hora para alarmas.
      'a las 7'        → '07:00'
      'a las 7:30'     → '07:30'
      'a las siete'    → '07:00'
    """
    # Formato digital: "a las 7:30" o "a las 7"
    m = re.search(r"a\s+las?\s+(\d{1,2})(?::(\d{2}))?", text, re.IGNORECASE)
    if m:
        h = int(m.group(1))
        mins = m.group(2) or "00"
        return f"{h:02d}:{mins}"

    # Formato palabra: "a las siete"
    m = re.search(rf"a\s+las?\s+({_WORD_NUM_RE})", text, re.IGNORECASE)
    if m:
        v = _WORD_NUM.get(m.group(1).lower())
        if v is not None:
            return f"{v:02d}:00"

    return None


def _extract_temperature(text: str) -> Optional[int]:
    """
    Temperatura: '24 grados', 'veinticuatro grados'
    """
    m = re.search(rf"\b(\d+|{_WORD_NUM_RE})\s+grados?", text, re.IGNORECASE)
    if m:
        return _to_num(m.group(1))
    return None


def _extract_contact(text: str) -> Optional[str]:
    """
    Nombre de contacto despues de 'a', 'para', 'llama a'.
    Corta antes de 'diciendo', 'con asunto', 'sobre', etc.
    """
    email = re.search(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", text)
    if email:
        return email.group(0)

    trimmed = re.sub(
        r"\s+(diciendo|que diga|que dice|con asunto|sobre|con el mensaje).*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    m = re.search(
        r"\b(?:llama\s+a|envia(?:le)?\s+(?:un\s+\w+\s+)?a|manda(?:le)?\s+(?:un\s+\w+\s+)?a|para|a)\s+"
        r"([A-Za-záéíóúüñÁÉÍÓÚÜÑ][A-Za-záéíóúüñÁÉÍÓÚÜÑ\s]{1,30})",
        trimmed,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    return None


def _extract_query(text: str) -> Optional[str]:
    """
    Query de busqueda: 'busca [query]', 'busca en la web [query]'
    """
    m = re.search(r"\bbusca(?:\s+en\s+(?:la\s+)?web)?\s+(.+)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def _extract_youtube_query(text: str) -> Optional[str]:
    """
    Query para abrir contenido en YouTube:
      'abri youtube un video de rocket league' -> 'rocket league'
      'abre youtube y busca the weekend' -> 'the weekend'
    """
    m = re.search(r"\byoutube\b(?:\s+y\s+busca)?\s+(.+)", text, re.IGNORECASE)
    if not m:
        return None

    query = m.group(1).strip()
    query = re.sub(r"^(un\s+video\s+de|video\s+de)\s+", "", query, flags=re.IGNORECASE)
    query = re.sub(r"^(la\s+cancion\s+|cancion\s+de\s+)", "", query, flags=re.IGNORECASE)
    return query.strip() or None


def _extract_video_query(text: str) -> Optional[str]:
    """
    Query cuando el usuario pide un video sin mencionar YouTube.
      'abri un video de rocket league' -> 'rocket league'
      'abrime un video del rubius por favor' -> 'rubius'
    """
    m = re.search(
        r"\b(?:abre|abri|abrime|abrir|pon|poneme|reproduce|busca)\b.*?\bvideo\b\s+"
        r"(?:del|de|sobre)?\s*(.+)",
        text,
        re.IGNORECASE,
    )
    if not m:
        return None

    query = m.group(1).strip()
    query = re.sub(r"\b(por\s+favor|porfa|gracias)\b", "", query, flags=re.IGNORECASE).strip()
    query = re.sub(r"\s+", " ", query)
    return query or None


def _extract_capture_source(text: str) -> str:
    """
    Distingue entre foto de camara y captura de pantalla.
    """
    if re.search(r"\b(foto|camara|selfie|sacame\s+una\s+foto|tomame\s+una\s+foto)\b", text, re.IGNORECASE):
        return "camera"
    return "screen"


def _extract_filename(text: str) -> Optional[str]:
    """
    Nombre de archivo o carpeta: 'llamado X', 'llamada X', 'con nombre X', 'de nombre X'
    """
    m = re.search(
        r"\b(?:llamad[oa]|con nombre|de nombre)\s+([^\s,\.]+)",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    return None


def _extract_city(text: str) -> Optional[str]:
    """
    Ciudad: 'el clima en Buenos Aires', 'clima de Madrid'
    """
    m = re.search(
        r"\b(?:clima\s+(?:en|de)|tiempo\s+(?:en|de)|en\s+la\s+ciudad\s+de)\s+"
        r"([A-Za-záéíóúüñÁÉÍÓÚÜÑ][A-Za-záéíóúüñÁÉÍÓÚÜÑ\s]{2,25})",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    return None


def _extract_message(text: str) -> Optional[str]:
    """
    Cuerpo del mensaje: 'diciendo X', 'que diga X', 'con el mensaje X'
    """
    m = re.search(
        r"\b(?:diciendo|que diga|que dice|con el mensaje)\s+(.+)",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    return None


def _extract_subject(text: str) -> Optional[str]:
    """
    Asunto de email: 'con asunto X', 'sobre X'
    """
    m = re.search(
        r"\b(?:con asunto|sobre)\s+(.+?)(?:\s+(?:diciendo|con el cuerpo|y\s+dile)|$)",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    return None


# ── Grupos de intents ────────────────────────────────────────────────────────

_VOLUME_INTENTS = {"volume_up", "volume_down", "set_volume"}
_BRIGHTNESS_INTENTS = {"brightness_up", "brightness_down", "set_brightness"}
_LIGHTS_INTENTS = {"smart_lights_dim", "smart_lights_brighten"}
_SEEK_INTENTS = {"media_seek_forward", "media_seek_backward"}
_FILE_INTENTS = {"create_file", "delete_file", "rename_file", "move_file", "copy_file"}
_FOLDER_INTENTS = {"create_folder", "delete_folder"}


# ── API publica ──────────────────────────────────────────────────────────────

def extract_entities(text: str, intent: str) -> dict:
    """
    Extrae entidades del texto crudo dado el intent clasificado.
    Retorna un dict (puede estar vacio si no hay entidades relevantes).
    """
    entities: dict = {}

    if intent in _VOLUME_INTENTS | _BRIGHTNESS_INTENTS | _LIGHTS_INTENTS:
        v = _extract_value(text)
        if v is not None:
            entities["value"] = v

    elif intent == "thermostat_set_temp":
        t = _extract_temperature(text)
        if t is not None:
            entities["temperature"] = t

    elif intent == "start_timer":
        d = _extract_duration_seconds(text)
        if d is not None:
            entities["duration_seconds"] = d

    elif intent == "set_alarm":
        t = _extract_time(text)
        if t is not None:
            entities["time"] = t

    elif intent in _SEEK_INTENTS:
        v = _first_number(text)
        if v is not None:
            entities["seconds"] = v

    elif intent == "browser_search_web":
        q = _extract_query(text)
        if q:
            entities["query"] = q

    elif intent == "open_youtube":
        q = _extract_youtube_query(text)
        if not q:
            q = _extract_video_query(text)
        if q:
            entities["query"] = q

    elif intent == "take_screenshot":
        entities["source"] = _extract_capture_source(text)

    elif intent == "send_email":
        c = _extract_contact(text)
        if c:
            entities["contact"] = c
        s = _extract_subject(text)
        if s:
            entities["subject"] = s
        msg = _extract_message(text)
        if msg:
            entities["body"] = msg

    elif intent == "send_whatsapp_message":
        c = _extract_contact(text)
        if c:
            entities["contact"] = c
        msg = _extract_message(text)
        if msg:
            entities["message"] = msg

    elif intent == "call_contact":
        c = _extract_contact(text)
        if c:
            entities["contact"] = c

    elif intent in _FILE_INTENTS:
        f = _extract_filename(text)
        if f:
            entities["filename"] = f

    elif intent in _FOLDER_INTENTS:
        f = _extract_filename(text)
        if f:
            entities["folder_name"] = f

    elif intent == "get_weather":
        city = _extract_city(text)
        if city:
            entities["city"] = city

    return entities
