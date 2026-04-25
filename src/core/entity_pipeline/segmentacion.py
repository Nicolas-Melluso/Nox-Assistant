import re
from .nlp_singleton import get_spacy_model

def segmentar_frases(text):
    """
    Segmenta el texto en frases u oraciones usando spaCy y reglas adicionales para comandos pegados.
    Devuelve una lista de frases.
    """
    nlp = get_spacy_model()
    doc = nlp(text)
    oraciones = [sent.text.strip() for sent in doc.sents]
    resultado = []
    for oracion in oraciones:
        partes = re.split(r"\b(?:y|luego|después|despues|entonces|;|\.)\b", oracion, flags=re.IGNORECASE)
        for p in partes:
            frase = p.strip()
            frase = re.sub(r'^(y|luego|después|despues|entonces)\s+', '', frase, flags=re.IGNORECASE)
            frase = re.sub(r'[\.;:,!?¡¿]+$', '', frase).strip()
            if frase:
                resultado.append(frase)
    return resultado
