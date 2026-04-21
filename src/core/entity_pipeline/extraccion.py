from .nlp_singleton import nlp

def extraer_entidades_base(text):
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
