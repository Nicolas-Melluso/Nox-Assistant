from .nlp_singleton import nlp

def extraer_sujeto_verbo_objeto(texto):
    """
    Extrae tripletas (sujeto, verbo, objeto) usando dependencias gramaticales de spaCy.
    Devuelve una lista de dicts con las tripletas encontradas.
    """
    # Segmentar manualmente por conectores comunes antes de procesar con spaCy
    import re
    frases = re.split(r"\b(?:y|luego|después|despues|entonces|;|\.)\b", texto, flags=re.IGNORECASE)
    tripletas = []
    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
        doc = nlp(frase)
        for sent in doc.sents:
            sujeto = None
            verbo = None
            objeto = None
            for token in sent:
                if token.dep_ in ("nsubj", "nsubj:pass"):
                    sujeto = token.text
                if token.pos_ == "VERB":
                    verbo = token.text
                if token.dep_ in ("obj", "dobj", "iobj"):
                    objeto = token.text
            # Heurística: si no se detectó verbo, probar con el primer token si la frase es corta y parece imperativo
            if not verbo and len(sent) <= 5:
                primer = sent[0]
                if primer.text[0].isupper() and primer.pos_ in ("PROPN", "NOUN"):
                    verbo = primer.text
            # Si no se detectó objeto por dependencias, usar noun_chunks (para imperativos)
            if not objeto and verbo:
                for chunk in sent.noun_chunks:
                    if verbo.lower() not in chunk.text.lower():
                        objeto = chunk.root.text
                        break
            # Heurística final: si sigue sin objeto, tomar el último sustantivo (NOUN) de la frase
            if not objeto and verbo:
                nouns = [t.text for t in sent if t.pos_ == "NOUN"]
                if nouns:
                    objeto = nouns[-1]
            if verbo:
                tripletas.append({"sujeto": sujeto, "verbo": verbo, "objeto": objeto})
    return tripletas
