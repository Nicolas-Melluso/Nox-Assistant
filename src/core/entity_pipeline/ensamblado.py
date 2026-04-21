import re
from .extraccion import extraer_entidades_base
from .postprocesamiento import postprocesar_entidades
from .desambiguacion import desambiguar_entidades_por_contexto

def ensamblar_output(frases, negaciones_regex, nlp, limpiar_texto_func):
    resultados = []
    for frase in frases:
        frase_lower = frase.lower()
        es_negacion = any(re.search(neg, frase_lower) for neg in negaciones_regex)
        frase_strip = frase.strip()
        es_pregunta = (
            frase_strip.endswith("?")
            or frase_strip.startswith("¿")
            or "?" in frase_strip
            or "¿" in frase_strip
        )
        entities = extraer_entidades_base(frase)
        entities = postprocesar_entidades(entities, frase)
        entities = desambiguar_entidades_por_contexto(entities, frase)
        resultados.append({
            "frase": frase,
            "negacion": es_negacion,
            "pregunta": es_pregunta,
            "entidades": entities
        })
    return resultados
