from .nlp_singleton import get_spacy_model


def extraer_entidades_base(text, nlp=None):
    model = nlp or get_spacy_model()
    doc = model(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
