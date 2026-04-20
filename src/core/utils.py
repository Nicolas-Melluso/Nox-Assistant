import unicodedata
import re

def limpiar_y_normalizar(texto: str) -> str:
    """
    Limpia y normaliza el texto:
    - Pasa a minúsculas
    - Elimina tildes/acentos
    - Corrige espacios y caracteres especiales
    - Normaliza palabras comunes (ej: "prendé" → "prende")
    """
    # Pasar a minúsculas
    texto = texto.lower()
    # Eliminar tildes/acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Corregir espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    # Normalizar palabras comunes (puedes expandir este diccionario)
    normalizaciones = {
        "prende": ["prende", "prendé", "enciende", "encendé"],
        "apaga": ["apaga", "apagá", "desactiva", "desactivá"],
        "sube": ["sube", "subí", "aumenta", "aumentá"],
        "baja": ["baja", "bajá", "disminuye", "disminuí"],
    }
    for canonica, variantes in normalizaciones.items():
        for variante in variantes:
            texto = re.sub(rf'\b{variante}\b', canonica, texto)
    return texto


# --- Lematización y Stemming ---
import spacy
from typing import List

try:
    nlp_es = spacy.load("es_core_news_sm")
except Exception:
    nlp_es = None  # Para evitar error si no está instalado

def lematizar(texto: str) -> List[str]:
    """
    Devuelve una lista de lemas para cada token del texto usando spaCy.
    """
    if nlp_es is None:
        return texto.split()
    doc = nlp_es(texto)
    return [token.lemma_ for token in doc]

# Stemming con NLTK (Snowball para español)
try:
    from nltk.stem.snowball import SnowballStemmer
    stemmer_es = SnowballStemmer("spanish")
except ImportError:
    stemmer_es = None

def stemmizar(texto: str) -> List[str]:
    """
    Devuelve una lista de raíces (stems) para cada token del texto usando NLTK.
    """
    if stemmer_es is None:
        return texto.split()
    tokens = texto.split()
    return [stemmer_es.stem(token) for token in tokens]
