# Diccionario ampliado de sinónimos/variantes para comandos y dispositivos
SINONIMOS_COMANDO = {
    "prende": ["prende", "prendé", "enciende", "encendé", "enciéndeme", "activa", "actívalo", "activalo"],
    "apaga": ["apaga", "apagá", "desactiva", "desactívalo", "desactivalo", "apágame"],
    "sube": ["sube", "subí", "aumenta", "aumentá", "incrementa", "alza"],
    "baja": ["baja", "bajá", "reduce", "disminuye", "disminuí"],
    "abre": ["abre", "abrí", "ábreme"],
    "cierra": ["cierra", "cerrá", "ciérrame"],
    "pon": ["pon", "poné", "coloca"],
    "reproduce": ["reproduce", "pon", "poné", "coloca"],
    "pausa": ["pausa", "detén", "pará", "deten"],
    "reserva": ["reserva", "reservá", "aparta"],
    "crea": ["crea", "creá", "genera", "agrega", "anota"],
}

SINONIMOS_DISPOSITIVO = {
    "luz": ["luz", "luces", "lucecitas", "iluminación", "iluminacion"],
    "foco": ["foco", "focos", "bombilla", "bombillas"],
    "lampara": ["lampara", "lámpara"],
    "televisor": ["tele", "televisor", "tv", "pantalla", "pantallón", "monitor", "smart tv"],
    "puerta": ["puerta", "puertita", "portón", "porton"],
    "ventana": ["ventana", "ventanita", "persiana"],
    "impresora": ["impresora", "impresora 3d", "printer", "plotter"],
    "camara": ["cámara", "camara", "webcam", "camarita"],
    "auto": ["auto", "vehículo", "vehiculo", "coche", "carro", "automóvil", "automovil"],
    "musica": ["música", "musica", "radio", "parlante", "altavoz", "bocina", "speaker"],
    "nota": ["notas", "nota", "recordatorio", "apunte", "memo"],
    "clima": ["clima", "tiempo", "temperatura", "ambiente"],
    "noticias": ["noticias", "news", "informativo", "boletín", "boletin"],
    "contacto": ["contactos", "contacto", "agenda", "teléfonos", "telefonos"],
    "modelo": ["modelo", "modelo 3d", "maqueta", "prototipo"],
    "alarma": ["sistema de seguridad", "alarma", "sensor", "alarma antirrobo"],
    "ventilador": ["ventilador", "calefacción", "calefaccion", "aire", "ac", "aire acondicionado"],
    "brillo": ["brillo", "pantalla", "contraste"],
}

def normalizar_entidad_sinonimos(texto: str, tipo: str) -> str:
    """
    Normaliza una entidad extraída a su forma canónica usando los diccionarios de sinónimos.
    tipo: "COMANDO" o "DISPOSITIVO"
    """
    texto_limpio = texto.lower().strip()
    if tipo == "COMANDO":
        # Si el texto es exactamente un sinónimo
        for canonica, variantes in SINONIMOS_COMANDO.items():
            if texto_limpio in variantes:
                return canonica
        # Si es una frase, buscar el primer verbo conocido
        tokens = texto_limpio.split()
        for token in tokens:
            for canonica, variantes in SINONIMOS_COMANDO.items():
                if token in variantes:
                    return canonica
    elif tipo == "DISPOSITIVO":
        for canonica, variantes in SINONIMOS_DISPOSITIVO.items():
            if texto_limpio in variantes:
                return canonica
        # Si es una frase, buscar el primer término conocido
        tokens = texto_limpio.split()
        for token in tokens:
            for canonica, variantes in SINONIMOS_DISPOSITIVO.items():
                if token in variantes:
                    return canonica
    return texto
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
